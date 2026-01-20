# Benchmark-Report: Windkraft-Visualisierung

**Datum:** 2026-01-19T00:38:05.280700

## System-Informationen

| Parameter | Wert |
|-----------|------|
| timestamp | 2026-01-19T00:38:05.280700 |
| platform | Windows-10-10.0.22631-SP0 |
| processor | Intel64 Family 6 Model 142 Stepping 12, GenuineIntel |
| machine | AMD64 |
| cpu_name | Intel(R) Core(TM) i7-8665U CPU @ 1.90GHz |
| cpu_numberofcores | 4 |
| cpu_numberoflogicalprocessors | 8 |
| ram_gb | 15.8 |
| gpu | Intel(R) UHD Graphics 620 |
| numpy_version | 1.26.4 |

## Test-Ergebnisse

### Baseline

```json
{
  "n_1000": {
    "dataset_size": 1000,
    "frustum_tests": {
      "frustum_0.5": {
        "mean_ms": 0.5989720001525711,
        "std_ms": 0.1289429701267683,
        "min_ms": 0.38189999759197235,
        "max_ms": 0.834399997984292,
        "median_ms": 0.6514500018965919,
        "p5_ms": 0.3923100019164849,
        "p95_ms": 0.7813600001099984,
        "iterations": 50,
        "result_count": 99,
        "extra": {}
      },
      "frustum_1.0": {
        "mean_ms": 0.6967279998207232,
        "std_ms": 0.09298061527174875,
        "min_ms": 0.6516000030387659,
        "max_ms": 1.2210999993840232,
        "median_ms": 0.6607000013900688,
        "p5_ms": 0.6564250001247274,
        "p95_ms": 0.8457950008960322,
        "iterations": 50,
        "result_count": 403,
        "extra": {}
      },
      "frustum_1.5": {
        "mean_ms": 1.2558199996419717,
        "std_ms": 0.32976932188055075,
        "min_ms": 1.0451999987708405,
        "max_ms": 2.1846999989065807,
        "median_ms": 1.0734499974205391,
        "p5_ms": 1.0514649999095127,
        "p95_ms": 1.9194750000679048,
        "iterations": 50,
        "result_count": 871,
        "extra": {}
      }
    }
  },
  "n_5000": {
    "dataset_size": 5000,
    "frustum_tests": {
      "frustum_0.5": {
        "mean_ms": 2.1097479998570634,
        "std_ms": 0.45257772005306673,
        "min_ms": 1.7384999991918448,
        "max_ms": 3.680600002553547,
        "median_ms": 1.9054999993386446,
        "p5_ms": 1.7449249991841498,
        "p95_ms": 2.9493049996744958,
        "iterations": 50,
        "result_count": 513,
        "extra": {}
      },
      "frustum_1.0": {
        "mean_ms": 4.108730000152718,
        "std_ms": 1.0594033928402553,
        "min_ms": 3.138800002489006,
        "max_ms": 6.789200000639539,
        "median_ms": 3.632199999628938,
        "p5_ms": 3.169780000098399,
        "p95_ms": 6.2956199999462115,
        "iterations": 50,
        "result_count": 2116,
        "extra
... (gekürzt)
```

### Octree Parameters

```json
{
  "max_turbines_variation": {
    "max_t_4": {
      "max_turbines": 4,
      "build_time_ms": 789.0728799997305,
      "build_time_std": 162.6284451500823,
      "query_small_ms": 8.110253999984707,
      "query_large_ms": 38.976827999722445,
      "visible_small": 3129,
      "visible_large": 12652,
      "nodes": 21505,
      "leaves": 16129,
      "max_depth": 9,
      "avg_per_leaf": 1.86000372000744
    },
    "max_t_8": {
      "max_turbines": 8,
      "build_time_ms": 707.2036099991237,
      "build_time_std": 176.74004211782128,
      "query_small_ms": 4.788077999910456,
      "query_large_ms": 16.809707999564125,
      "visible_small": 3129,
      "visible_large": 12652,
      "nodes": 12065,
      "leaves": 9049,
      "max_depth": 8,
      "avg_per_leaf": 3.3152834567355507
    },
    "max_t_16": {
      "max_turbines": 16,
      "build_time_ms": 432.34797000041,
      "build_time_std": 304.8365370296881,
      "query_small_ms": 2.4323540001932997,
      "query_large_ms": 10.846296000454458,
      "visible_small": 3129,
      "visible_large": 12652,
      "nodes": 4577,
      "leaves": 3433,
      "max_depth": 7,
      "avg_per_leaf": 8.73871249635887
    },
    "max_t_32": {
      "max_turbines": 32,
      "build_time_ms": 260.4432599997381,
      "build_time_std": 29.722414887500307,
      "query_small_ms": 2.819716000012704,
      "query_large_ms": 10.5133940003725,
      "visible_small": 3129,
      "visible_large": 12652,
      "nodes": 3581,
      "leaves": 2686,
      "max_depth": 6,
      "avg_per_leaf": 11.169024571854058
    },
    "max_t_64": {
      "max_turbines": 64,
      "build_time_ms": 196.05085000002873,
      "build_time_std": 8.537406939690209,
      "query_small_ms": 2.337240000051679,
      "query_large_ms": 9.07788399963465,
      "visible_small": 3129,
      "visible_large": 12652,
      "nodes": 1125,
      "leaves": 844,
      "max_depth": 5,
      "avg_per_leaf": 35.54502369668246
    }
  }
}
```

### Octree Vs Linear

```json
{
  "frustum_0.1": {
    "frustum_size": 0.1,
    "visible_count": 134,
    "visible_ratio": 0.0044666666666666665,
    "octree_ms": 0.2542899996478809,
    "linear_ms": 3.0288200001814403,
    "speedup": 11.910889159524526,
    "octree_faster": true
  },
  "frustum_0.25": {
    "frustum_size": 0.25,
    "visible_count": 756,
    "visible_ratio": 0.0252,
    "octree_ms": 0.8316979999653995,
    "linear_ms": 3.373400000127731,
    "speedup": 4.056039572378522,
    "octree_faster": true
  },
  "frustum_0.5": {
    "frustum_size": 0.5,
    "visible_count": 3129,
    "visible_ratio": 0.1043,
    "octree_ms": 3.561116000273614,
    "linear_ms": 4.481909999958589,
    "speedup": 1.2585689428859455,
    "octree_faster": true
  },
  "frustum_0.75": {
    "frustum_size": 0.75,
    "visible_count": 7073,
    "visible_ratio": 0.23576666666666668,
    "octree_ms": 7.3399719998269575,
    "linear_ms": 3.599241999836522,
    "speedup": 0.4903618160834095,
    "octree_faster": false
  },
  "frustum_1.0": {
    "frustum_size": 1.0,
    "visible_count": 12652,
    "visible_ratio": 0.42173333333333335,
    "octree_ms": 13.197908000074676,
    "linear_ms": 3.9689540002291324,
    "speedup": 0.3007259938625633,
    "octree_faster": false
  },
  "frustum_1.5": {
    "frustum_size": 1.5,
    "visible_count": 26490,
    "visible_ratio": 0.883,
    "octree_ms": 28.19403199988301,
    "linear_ms": 4.298198000178672,
    "speedup": 0.15245063211237428,
    "octree_faster": false
  },
  "frustum_2.0": {
    "frustum_size": 2.0,
    "visible_count": 30000,
    "visible_ratio": 1.0,
    "octree_ms": 34.80153399963456,
    "linear_ms": 6.137085999944247,
    "speedup": 0.1763452725965669,
    "octree_faster": false
  },
  "frustum_3.0": {
    "frustum_size": 3.0,
    "visible_count": 30000,
    "visible_ratio": 1.0,
    "octree_ms": 33.67807200003881,
    "linear_ms": 7.873384000049555,
    "speedup": 0.2337836916567101,
    "octree_faster": false
  },
  "analysis": {
    "break_even_frustum_siz
```

### Numpy Vs Python

```json
{
  "n_1000": {
    "year_filter": {
      "python_ms": 0.10124999995847854,
      "numpy_ms": 0.005473333294503391,
      "speedup": 18.498782096854786
    },
    "bbox_check": {
      "python_ms": 0.20875666668871418,
      "numpy_ms": 0.016323333450903494,
      "speedup": 12.78885022575824
    },
    "distance": {
      "python_ms": 1.114420000400666,
      "numpy_ms": 0.027829999453388155,
      "speedup": 40.043838386241546
    },
    "combined": {
      "python_ms": 0.13844666658163382,
      "numpy_ms": 0.024599999718096417,
      "speedup": 5.627913340169218,
      "result_count": 93
    },
    "power_sum": {
      "python_ms": 0.10534333329511962,
      "numpy_ms": 0.01729333331847253,
      "speedup": 6.091557443271688
    }
  },
  "n_5000": {
    "year_filter": {
      "python_ms": 0.48220000038175687,
      "numpy_ms": 0.020573333191957015,
      "speedup": 23.438107762249686
    },
    "bbox_check": {
      "python_ms": 0.771070000337204,
      "numpy_ms": 0.03176999986559773,
      "speedup": 24.27038097573806
    },
    "distance": {
      "python_ms": 5.914196666829715,
      "numpy_ms": 0.03537000023546474,
      "speedup": 167.20940422555262
    },
    "combined": {
      "python_ms": 0.9313299999727557,
      "numpy_ms": 0.03633666650178687,
      "speedup": 25.63058446561016,
      "result_count": 421
    },
    "power_sum": {
      "python_ms": 0.6856566667314231,
      "numpy_ms": 0.05762333300178094,
      "speedup": 11.898941470640578
    }
  },
  "n_10000": {
    "year_filter": {
      "python_ms": 1.1653266665234696,
      "numpy_ms": 0.02309666730676933,
      "speedup": 50.45432100855207
    },
    "bbox_check": {
      "python_ms": 3.7154733334318735,
      "numpy_ms": 0.04861999999169105,
      "speedup": 76.41862061017754
    },
    "distance": {
      "python_ms": 10.307686666419613,
      "numpy_ms": 0.03189333341045616,
      "speedup": 323.1925159331342
    },
    "combined": {
      "python_ms": 12.167016666959777,
      "numpy_m
... (gekürzt)
```

### Lod System

```json
{
  "camera_positions": {
    "cam_0.0_0.0": {
      "camera_pos": [
        0.0,
        0.0
      ],
      "update_time_ms": 915.3980539998156,
      "lod_distribution": {
        "0": 898,
        "1": 5301,
        "2": 20300
      },
      "vertices_with_lod": 2973200,
      "vertices_without_lod": 26499000,
      "vertex_reduction": 0.8877995396052681
    },
    "cam_-1.0_-1.0": {
      "camera_pos": [
        -1.0,
        -1.0
      ],
      "update_time_ms": 748.4298000003037,
      "lod_distribution": {
        "0": 866,
        "1": 3464,
        "2": 22169
      },
      "vertices_with_lod": 2667250,
      "vertices_without_lod": 26499000,
      "vertex_reduction": 0.8993452583116344
    },
    "cam_1.0_1.0": {
      "camera_pos": [
        1.0,
        1.0
      ],
      "update_time_ms": 57.874466000212124,
      "lod_distribution": {
        "0": 953,
        "1": 3455,
        "2": 22091
      },
      "vertices_with_lod": 2748550,
      "vertices_without_lod": 26499000,
      "vertex_reduction": 0.8962772180082267
    },
    "cam_0.0_-1.5": {
      "camera_pos": [
        0.0,
        -1.5
      ],
      "update_time_ms": 89.0294140001788,
      "lod_distribution": {
        "0": 447,
        "1": 2740,
        "2": 23312
      },
      "vertices_with_lod": 2160600,
      "vertices_without_lod": 26499000,
      "vertex_reduction": 0.9184648477301031
    },
    "cam_0.5_0.5": {
      "camera_pos": [
        0.5,
        0.5
      ],
      "update_time_ms": 83.80157599996892,
      "lod_distribution": {
        "0": 892,
        "1": 5503,
        "2": 20104
      },
      "vertices_with_lod": 2997800,
      "vertices_without_lod": 26499000,
      "vertex_reduction": 0.8868712026868939
    }
  }
}
```

### Scalability

```json
{
  "n_1000": {
    "dataset_size": 1000,
    "legacy_ms": 0.23015666641488983,
    "numpy_ms": 0.08862333318878275,
    "octree_ms": 0.33780666684227373,
    "octree_build_ms": 14.425500001379987,
    "result_count": 89,
    "numpy_speedup": 2.597021101932795,
    "octree_speedup": 0.6813265959678437
  },
  "n_2500": {
    "dataset_size": 2500,
    "legacy_ms": 0.5914633335729983,
    "numpy_ms": 0.19841666653519496,
    "octree_ms": 1.0649633331922814,
    "octree_build_ms": 49.20239999773912,
    "result_count": 204,
    "numpy_speedup": 2.9809155848714206,
    "octree_speedup": 0.5553837537298651
  },
  "n_5000": {
    "dataset_size": 5000,
    "legacy_ms": 1.8703866663903075,
    "numpy_ms": 0.3381766668705192,
    "octree_ms": 2.6122699998571384,
    "octree_build_ms": 136.03460000013,
    "result_count": 402,
    "numpy_speedup": 5.5307975079973195,
    "octree_speedup": 0.7160005154492439
  },
  "n_10000": {
    "dataset_size": 10000,
    "legacy_ms": 3.732356666296255,
    "numpy_ms": 1.6685733331541996,
    "octree_ms": 7.563819999874492,
    "octree_build_ms": 404.43470000172965,
    "result_count": 815,
    "numpy_speedup": 2.2368550378548644,
    "octree_speedup": 0.4934486365828624
  },
  "n_15000": {
    "dataset_size": 15000,
    "legacy_ms": 4.1796666669445885,
    "numpy_ms": 0.7670466663209178,
    "octree_ms": 7.151783333150282,
    "octree_build_ms": 465.68869999828166,
    "result_count": 1259,
    "numpy_speedup": 5.4490383055727865,
    "octree_speedup": 0.5844229994455791
  },
  "n_20000": {
    "dataset_size": 20000,
    "legacy_ms": 7.865806666571491,
    "numpy_ms": 0.929083333176095,
    "octree_ms": 14.042926666418984,
    "octree_build_ms": 692.3138000020117,
    "result_count": 1604,
    "numpy_speedup": 8.466201454375499,
    "octree_speedup": 0.560125880695588
  },
  "n_25000": {
    "dataset_size": 25000,
    "legacy_ms": 7.168656666302316,
    "numpy_ms": 1.2134533331845887,
    "octree_ms": 7.7942733329109615,
    "octree_build_m
... (gekürzt)
```

### Distributions

```json
{
  "uniform": {
    "distribution_stats": {
      "x_mean": -0.0011761596524403359,
      "x_std": 0.8061712558418838,
      "z_mean": -0.0014486519085082758,
      "z_std": 0.9821620764599205
    },
    "octree_build_ms": 1020.7351999997627,
    "octree_nodes": 12065,
    "octree_leaves": 9049,
    "octree_max_depth": 8,
    "query_time_ms": 7.611294000162161,
    "visible_count": 3129
  },
  "clustered": {
    "distribution_stats": {
      "x_mean": -0.0998454057471298,
      "x_std": 0.7416567835812833,
      "z_mean": -0.009793783282961962,
      "z_std": 0.7093597303606098
    },
    "octree_build_ms": 588.3045999980823,
    "octree_nodes": 10797,
    "octree_leaves": 8098,
    "octree_max_depth": 9,
    "query_time_ms": 5.669634000005317,
    "visible_count": 3927
  },
  "realistic": {
    "distribution_stats": {
      "x_mean": 0.009954441877886024,
      "x_std": 0.8080281154886017,
      "z_mean": -0.7321296407748198,
      "z_std": 0.5385417502877756
    },
    "octree_build_ms": 423.9912999983062,
    "octree_nodes": 10221,
    "octree_leaves": 7666,
    "octree_max_depth": 9,
    "query_time_ms": 4.498978000046918,
    "visible_count": 3035
  }
}
```

### Combinations

```json
{
  "keine_optimierung": {
    "octree": false,
    "lod": false,
    "cache": false,
    "time_ms": 31.766337999797543,
    "visible_count": 12591,
    "speedup": 1.0
  },
  "nur_octree": {
    "octree": true,
    "lod": false,
    "cache": false,
    "time_ms": 33.148282000183826,
    "visible_count": 12591,
    "speedup": 0.9583102376051157
  },
  "nur_lod": {
    "octree": false,
    "lod": true,
    "cache": false,
    "time_ms": 55.443076000519795,
    "visible_count": 12591,
    "speedup": 0.5729541052069284
  },
  "nur_cache_numpy": {
    "octree": false,
    "lod": false,
    "cache": true,
    "time_ms": 33.20112400004291,
    "visible_count": 12591,
    "speedup": 0.9567850172709962
  },
  "octree_+_lod": {
    "octree": true,
    "lod": true,
    "cache": false,
    "time_ms": 51.271532000391744,
    "visible_count": 12591,
    "speedup": 0.6195706810468395
  },
  "octree_+_cache": {
    "octree": true,
    "lod": false,
    "cache": true,
    "time_ms": 34.71049200015841,
    "visible_count": 12591,
    "speedup": 0.9151797099174672
  },
  "lod_+_cache": {
    "octree": false,
    "lod": true,
    "cache": true,
    "time_ms": 52.83194000010553,
    "visible_count": 12591,
    "speedup": 0.6012714657030215
  },
  "alle_optimierungen": {
    "octree": true,
    "lod": true,
    "cache": true,
    "time_ms": 53.84607199979655,
    "visible_count": 12591,
    "speedup": 0.5899471738610306
  }
}
```

### Edge Cases

```json
{
  "empty_frustum": {
    "time_ms": 0.0009899998258333653,
    "result_count": 0
  },
  "full_frustum": {
    "time_ms": 41.265717999849585,
    "result_count": 30000
  },
  "tiny_frustum": {
    "time_ms": 0.1436479999392759,
    "result_count": 2
  },
  "single_year": {
    "year": 2020,
    "count": 805
  },
  "old_turbines": {
    "max_year": 1995,
    "time_ms": 11.165192000116804,
    "result_count": 4567
  }
}
```


---
*Gesamtlaufzeit: 261.3 Sekunden*
