import pandas as pd

import pandas as pd


def group_min_max(
    input_csv, output_csv, group_col, value_col, chunksize=100000
):
    result = None

    reader = pd.read_csv(
        input_csv,
        usecols=[group_col, value_col],
        dtype={group_col: "string", value_col: "string"},
        chunksize=chunksize,
    )

    for i, chunk in enumerate(reader):
        # 如果分组值首尾空格没有业务含义，可以启用：
        # chunk[group_col] = chunk[group_col].str.strip()

        chunk[value_col] = pd.to_datetime(
            chunk[value_col],
            format="%Y-%m-%d %H:%M:%S.%f",
            errors="coerce",
        )

        chunk = chunk.dropna(subset=[value_col])

        grouped = (
            chunk.groupby(group_col, dropna=False)[value_col]
            .agg(["min", "max"])
        )

        if result is None:
            result = grouped
        else:
            result = (
                pd.concat([result, grouped])
                .groupby(level=0, dropna=False)
                .agg({"min": "min", "max": "max"})
            )

        print(f"Chunk {i+1} done.")

    if result is None:
        result = pd.DataFrame(columns=["min", "max"])
        result.index.name = group_col

    result = result.rename(
        columns={
            "min": f"{value_col}_min",
            "max": f"{value_col}_max",
        }
    ).reset_index()

    # 输出时间保留三位毫秒，与输入格式一致
    for col in [f"{value_col}_min", f"{value_col}_max"]:
        result[col] = (
            pd.to_datetime(result[col])
            .dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            .str.slice(stop=-3)
        )

    result.to_csv(output_csv, index=False)
    return result

def rename_sort(input_csv, output_csv):

    df = pd.read_csv(input_csv)

    df.rename(columns={'patientid': 'subject_id'}, inplace=True)
    df.rename(columns={'observation_tables/_min': 'intime'}, inplace=True)
    df.rename(columns={'observation_tables/_max': 'outtime'}, inplace=True)

    df['subject_id'] = pd.to_numeric(df['subject_id'], errors='coerce')
    df = df.dropna(subset=['subject_id'])

    df.sort_values(by=['subject_id'], inplace=True)

    df.to_csv(output_csv, index=False)
    print(f"Done, result save to: {output_csv}")

    return df

if __name__ == "__main__":
    #group_min_max('../../hirid/observation_tables.csv', './stay_time.csv',
    #              'patientid', 'observation_tables/')
    rename_sort('./stay_time.csv', './stay_time.csv')