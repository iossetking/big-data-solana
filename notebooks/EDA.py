import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    from huggingface_hub import hf_hub_download
    import duckdb
    import polars as pl
    import pyarrow

    return duckdb, hf_hub_download, pl


@app.cell
def _(duckdb, hf_hub_download, pl):
    file_path = hf_hub_download(
        repo_id="solarchive/solarchive",
        filename="txs/2020-10-24/000000000000.parquet",
        repo_type="dataset"
    )

    df = pl.read_parquet(file_path)

    duckdb.sql("DESCRIBE SELECT * FROM df").show()
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
