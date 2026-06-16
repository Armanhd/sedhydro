
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 14:46:10 2026

@author: armanhaddadchi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches




def make_map_classes (lc,nodata, title):
    """
    Make a map from classified layers (e.g., land cover)
    
    """
    
    # ---- Get classes (exclude nodata) ----

    classes = np.unique(lc[np.isfinite(lc)])    
    classes = classes.astype(int)  # landcover classes usually ints
    print("Classes found:", classes)
    
    
    # If you don't know labels yet, this will just label by the integer code.
    class_labels = {c: f"Class {c}" for c in classes}
    
    # ---- Build a discrete colormap ----
    # (No need to manually pick colors; matplotlib will assign)
    cmap = plt.get_cmap('tab20', len(classes))
    listed = ListedColormap(cmap(np.arange(len(classes))))
    
    # Boundaries so each integer gets its own color bin
    bounds = np.arange(len(classes) + 1) - 0.5
    norm = BoundaryNorm(bounds, listed.N)
    
    # Remap raster values -> 0..N-1 for clean categorical plotting
    idx = np.full_like(lc, fill_value=-1, dtype=int)
    for i, c in enumerate(classes):
        idx[lc == c] = i
    
    # Mask nodata / outside
    idx_masked = np.ma.masked_where(idx < 0, idx)
    
    # ---- (1) Plot full landcover map with legend ----
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(idx_masked, cmap=listed, norm=norm)
    ax.set_title(title)
    ax.set_axis_off()
    
    legend_patches = [
        mpatches.Patch(color=listed(i), label=class_labels[classes[i]])
        for i in range(len(classes))
    ]
    ax.legend(handles=legend_patches, bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.tight_layout()
    #-----------------------
    import os

    # save_dir = "/Users/armanhaddadchi/Library/CloudStorage/OneDrive-UniversityofCalgary/ErosionModel"
    
    # # Clean title for filename
    # fname = title.replace(" ", "_").replace("/", "-")
    
    # plt.savefig(
    #     os.path.join(save_dir, f"{fname}.jpg"),
    #     dpi=300,
    #     bbox_inches="tight",
    #     format="jpg"
    # )
    plt.show()
   

def make_map_continuous (maplayer, title, label, cmaptype):
    plt.figure(figsize=(7, 6))
    plt.imshow(maplayer, cmap=cmaptype)
    plt.colorbar(label=label)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    import os

    # save_dir = "/Users/armanhaddadchi/Library/CloudStorage/OneDrive-UniversityofCalgary/ErosionModel"
    
    # # Clean title for filename
    # fname = title.replace(" ", "_").replace("/", "-")
    
    # plt.savefig(
    #     os.path.join(save_dir, f"{fname}.jpg"),
    #     dpi=300,
    #     bbox_inches="tight",
    #     format="jpg"
    # )
    plt.show()
    

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import Normalize, BoundaryNorm

def save_grid_with_attrs_and_plot(
    grid_gdf,
    slope_stats,
    landcover_erod_dominant,
    geol_erod_dominant,
    out_shp,
    write_shp=False,
    grid_id_col="grid_id",
    slope_cols_keep=("median_slope", "mean_slope", "min_slope", "max_slope", "std_dev_slope", "n_slope"),
    landcover_dom_col="dominant_class_landcover",
    geol_dom_col="dominant_class_geol",
    plot_col="median_slope",
    cmap="viridis",
    figsize=(8, 6),
    discrete_threshold=20,   # if <= this many unique integer-like values -> treat as discrete
):
    """
    Merge slope statistics + dominant landcover + dominant geology into a grid GeoDataFrame.
    Optionally write shapefile. Plot either:
      - Continuous variable -> colorbar
      - Discrete classes    -> legend with class numbers (higher = darker), same cmap

    Notes
    -----
    - Shapefile field names are constrained; this function renames to safe names.
    - Discrete plotting assumes classes are positive integers (or integer-like).
    """

    # Ensure GeoDataFrame
    out = gpd.GeoDataFrame(grid_gdf, geometry="geometry", crs=grid_gdf.crs).set_geometry("geometry")

    # Keep only needed columns from inputs
    slope_keep = [grid_id_col] + [c for c in slope_cols_keep if c in slope_stats.columns]
    slope_stats2 = slope_stats.loc[:, slope_keep].copy()

    landcover_dom2 = landcover_erod_dominant.loc[:, [grid_id_col, landcover_dom_col]].copy()
    geol_dom2      = geol_erod_dominant.loc[:, [grid_id_col, geol_dom_col]].copy()

    # Merge
    out = (
        out
        .merge(slope_stats2, on=grid_id_col, how="left")
        .merge(landcover_dom2, on=grid_id_col, how="left")
        .merge(geol_dom2, on=grid_id_col, how="left")
    )

    # Shapefile-safe names
    rename_map = {
        "median_slope": "slp_med",
        "mean_slope": "slp_mean",
        "min_slope": "slp_min",
        "max_slope": "slp_max",
        "std_dev_slope": "slp_std",
        "n_slope": "slp_n",
        landcover_dom_col: "lc_dom",
        geol_dom_col: "geo_dom",
    }
    out = out.rename(columns={k: v for k, v in rename_map.items() if k in out.columns})

    # Optional write
    if write_shp:
        os.makedirs(os.path.dirname(out_shp), exist_ok=True)
        out.to_file(out_shp, driver="ESRI Shapefile")

    # -----------------------------
    # Plot logic: continuous vs discrete
    # -----------------------------
    plot_field = rename_map.get(plot_col, plot_col)
    if plot_field not in out.columns:
        return out, out_shp

    vals = pd.to_numeric(out[plot_field], errors="coerce").to_numpy()

    # decide discrete if integer-like and limited unique values
    finite = np.isfinite(vals)
    uniq = np.unique(vals[finite])

    integer_like = np.allclose(uniq, np.round(uniq)) if uniq.size else False
    is_discrete = integer_like and (uniq.size <= discrete_threshold)

    fig, ax = plt.subplots(figsize=figsize)

    if not is_discrete:
        # -------- continuous: colorbar --------
        vmin, vmax = np.nanpercentile(vals, [2, 98])
        out.plot(
            column=plot_field,
            cmap=cmap,
            linewidth=0,
            edgecolor="none",
            vmin=vmin,
            vmax=vmax,
            legend=False,
            ax=ax
        )
        norm = Normalize(vmin=vmin, vmax=vmax)
        sm = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.get_cmap(cmap))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
        cbar.set_label(plot_field)

    else:
        # -------- discrete: class legend (higher = darker) --------
        classes = uniq.astype(int)
        classes = np.sort(classes)

        # Boundaries to force categorical bins; same cmap, ordered by class
        boundaries = np.arange(classes.min() - 0.5, classes.max() + 1.5, 1.0)
        norm = BoundaryNorm(boundaries, ncolors=mpl.cm.get_cmap(cmap).N, clip=True)

        out.plot(
            column=plot_field,
            cmap=cmap,
            linewidth=0,
            edgecolor="none",
            legend=False,
            norm=norm,
            ax=ax
        )

        # Build legend with class numbers; higher numbers get darker automatically via cmap+norm
        legend_handles = []
        cm = mpl.cm.get_cmap(cmap)
        for c in classes:
            color = cm(norm(c))
            legend_handles.append(mpl.patches.Patch(facecolor=color, edgecolor="none", label=str(c)))

        ax.legend(
            handles=legend_handles,
            title=plot_field,
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            borderaxespad=0
        )

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(plot_field)
    plt.tight_layout()
    plt.show()

    return out_shp

