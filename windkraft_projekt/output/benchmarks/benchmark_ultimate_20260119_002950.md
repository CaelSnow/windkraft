# Benchmark-Report: Windkraft-Visualisierung

**Datum:** 2026-01-19T00:29:08.843207

## System-Informationen

| Parameter | Wert |
|-----------|------|
| timestamp | 2026-01-19T00:29:08.843207 |
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
        "mean_ms": 0.21630400013236795,
        "std_ms": 0.021726803271703482,
        "min_ms": 0.19609999799286015,
        "max_ms": 0.2860999993572477,
        "median_ms": 0.20670000048994552,
        "p5_ms": 0.19743499924516072,
        "p95_ms": 0.26626000035321334,
        "iterations": 50,
        "result_count": 99,
        "extra": {}
      },
      "frustum_1.0": {
        "mean_ms": 0.479278000202612,
        "std_ms": 0.09274844555813963,
        "min_ms": 0.39599999945494346,
        "max_ms": 0.8705000000190921,
        "median_ms": 0.45449999925040174,
        "p5_ms": 0.40494499899068614,
        "p95_ms": 0.6889550011692335,
        "iterations": 50,
        "result_count": 403,
        "extra": {}
      },
      "frustum_1.5": {
        "mean_ms": 0.8343880000029458,
        "std_ms": 0.12176675025623457,
        "min_ms": 0.6658000020252075,
        "max_ms": 1.2062999994668644,
        "median_ms": 0.7988500001374632,
        "p5_ms": 0.7054700001390302,
        "p95_ms": 1.1025800009520021,
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
        "mean_ms": 1.0591140000178711,
        "std_ms": 0.16969339312705053,
        "min_ms": 0.9514000012131874,
        "max_ms": 1.7193999992741738,
        "median_ms": 0.9671500010881573,
        "p5_ms": 0.9526449997792952,
        "p95_ms": 1.3331350017324435,
        "iterations": 50,
        "result_count": 513,
        "extra": {}
      },
      "frustum_1.0": {
        "mean_ms": 1.8902839999645948,
        "std_ms": 0.24952123954016153,
        "min_ms": 1.6799000004539266,
        "max_ms": 2.711100001761224,
        "median_ms": 1.7879000006360002,
        "p5_ms": 1.682065001114097,
        "p95_ms": 2.435395000611606,
        "iterations": 50,
        "result_count": 2116,
 
... (gekürzt)
```

### Octree Parameters

❌ Fehler: OctreeNode.__init__() got an unexpected keyword argument 'max_depth'

### Octree Vs Linear

❌ Fehler: OctreeNode.__init__() got an unexpected keyword argument 'max_depth'

### Numpy Vs Python

```json
{
  "n_1000": {
    "year_filter": {
      "python_ms": 0.07585333357080042,
      "numpy_ms": 0.004096666695356059,
      "speedup": 18.515866486474724
    },
    "bbox_check": {
      "python_ms": 0.08714333343959879,
      "numpy_ms": 0.015316666637469703,
      "speedup": 5.689445066749509
    },
    "distance": {
      "python_ms": 0.7006266669729181,
      "numpy_ms": 0.009493334194606481,
      "speedup": 73.80195962878568
    },
    "combined": {
      "python_ms": 0.09818333358756111,
      "numpy_ms": 0.01665333341710114,
      "speedup": 5.895716558868486,
      "result_count": 93
    },
    "power_sum": {
      "python_ms": 0.09498000023692536,
      "numpy_ms": 0.01617666639504023,
      "speedup": 5.871419853601374
    }
  },
  "n_5000": {
    "year_filter": {
      "python_ms": 0.3381433336471673,
      "numpy_ms": 0.010533333503796408,
      "speedup": 32.102214700151116
    },
    "bbox_check": {
      "python_ms": 0.5687900000339141,
      "numpy_ms": 0.02650666598735067,
      "speedup": 21.458375802726312
    },
    "distance": {
      "python_ms": 3.042013333470095,
      "numpy_ms": 0.014739999824087135,
      "speedup": 206.37811192501084
    },
    "combined": {
      "python_ms": 0.5020000001726052,
      "numpy_ms": 0.02309666694297145,
      "speedup": 21.734737804900842,
      "result_count": 421
    },
    "power_sum": {
      "python_ms": 0.3658400004496798,
      "numpy_ms": 0.030703333201624144,
      "speedup": 11.915318706515148
    }
  },
  "n_10000": {
    "year_filter": {
      "python_ms": 0.7561166664042199,
      "numpy_ms": 0.01475000050656187,
      "speedup": 51.262145114357416
    },
    "bbox_check": {
      "python_ms": 1.0206566669997603,
      "numpy_ms": 0.033503333421928495,
      "speedup": 30.46433183665609
    },
    "distance": {
      "python_ms": 10.369106666500253,
      "numpy_ms": 0.050196666537279576,
      "speedup": 206.569626666333
    },
    "combined": {
      "python_ms": 2.0917233334330376,
      "nu
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
      "update_time_ms": 53.082049999866285,
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
      "update_time_ms": 34.40952599979937,
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
      "update_time_ms": 33.088625999880605,
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
      "update_time_ms": 33.47580799978459,
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
      "update_time_ms": 34.817135999692255,
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

❌ Fehler: OctreeNode.__init__() got an unexpected keyword argument 'max_depth'

### Distributions

❌ Fehler: OctreeNode.__init__() got an unexpected keyword argument 'max_depth'

### Combinations

```json
{
  "keine_optimierung": {
    "octree": false,
    "lod": false,
    "cache": false,
    "time_ms": 29.904550000355812,
    "visible_count": 12591,
    "speedup": 1.0
  },
  "nur_octree": {
    "octree": true,
    "lod": false,
    "cache": false,
    "time_ms": 22.261250000083237,
    "visible_count": 12591,
    "speedup": 1.3433454994775225
  },
  "nur_lod": {
    "octree": false,
    "lod": true,
    "cache": false,
    "time_ms": 39.483823999980814,
    "visible_count": 12591,
    "speedup": 0.7573873797120143
  },
  "nur_cache_numpy": {
    "octree": false,
    "lod": false,
    "cache": true,
    "time_ms": 22.911582000160706,
    "visible_count": 12591,
    "speedup": 1.3052154146381536
  },
  "octree_+_lod": {
    "octree": true,
    "lod": true,
    "cache": false,
    "time_ms": 43.258822000425425,
    "visible_count": 12591,
    "speedup": 0.6912936741564927
  },
  "octree_+_cache": {
    "octree": true,
    "lod": false,
    "cache": true,
    "time_ms": 22.466962000034982,
    "visible_count": 12591,
    "speedup": 1.331045559266502
  },
  "lod_+_cache": {
    "octree": false,
    "lod": true,
    "cache": true,
    "time_ms": 38.67947999991884,
    "visible_count": 12591,
    "speedup": 0.7731373327774458
  },
  "alle_optimierungen": {
    "octree": true,
    "lod": true,
    "cache": true,
    "time_ms": 39.66663400045945,
    "visible_count": 12591,
    "speedup": 0.7538968393438533
  }
}
```

### Edge Cases

❌ Fehler: OctreeNode.__init__() got an unexpected keyword argument 'max_depth'


---
*Gesamtlaufzeit: 41.2 Sekunden*
