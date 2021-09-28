from clumper import Clumper 
import pandas as pd
import numpy as np
from pathlib import Path

paths = Path("raw").glob("*/*/workflows/*.csv")

data = (Clumper.read_csv(list(paths), add_path=True)
        .mutate(date=lambda d: Path(d['read_path']).stem,
                org=lambda d: "/".join(Path(d['read_path']).parts[1:2]),
                repo=lambda d: "/".join(Path(d['read_path']).parts[2:3]),
                workflow=lambda d: d['name'])
        .collect())

pltr = (pd.DataFrame(data)
  .assign(updated_at=lambda d: pd.to_datetime(d['updated_at']),
          created_at=lambda d: pd.to_datetime(d['created_at']),
          time_taken = lambda d: (d['updated_at'] - d['created_at']).dt.seconds)
  .groupby(["date", "org", "repo", "workflow"])
  .agg(time_taken=("time_taken", "sum"))
  .reset_index())


(pltr
  .groupby(['org', 'repo', 'workflow', 'date'])
  .sum()
  .reset_index()
  .to_csv("all.csv", index=False))
