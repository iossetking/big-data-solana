import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    from huggingface_hub import hf_hub_download
    import duckdb
    import polars as pl
    import pyarrow


    return duckdb, hf_hub_download, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Dataset: https://huggingface.co/datasets/solarchive/solarchive
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Solana Transaction Schema

    Esquema de transacciones de Solana del dataset público de BigQuery (sin transacciones de voto).

    ## Campos principales

    | Campo | Tipo | Requerido | Descripción |
    |---|---|---|---|
    | `block_slot` | integer | Sí | Número de slot del bloque que contiene la transacción |
    | `block_hash` | string | Sí | Hash del bloque que contiene la transacción |
    | `block_timestamp` | string (date-time) | Sí | Marca de tiempo en que se produjo el bloque |
    | `recent_block_hash` | string | No | Blockhash reciente usado por la transacción |
    | `signature` | string | Sí | Firma única de la transacción (codificada en base58) |
    | `index` | integer | Sí | Índice de la transacción dentro del bloque |
    | `fee` | number | Sí | Comisión pagada en lamports (1 SOL = 1,000,000,000 lamports) |
    | `status` | string (`Success` \| `Failed`) | Sí | Estado de ejecución de la transacción |
    | `err` | string \| null | No | Mensaje de error si falló; `null` si fue exitosa |
    | `compute_units_consumed` | number | No | Unidades de cómputo consumidas por la transacción |
    | `log_messages` | array\<string\> | No | Mensajes de log de los programas emitidos durante la ejecución |
    | `accounts` | array\<object\> | No | Lista de cuentas involucradas (ver sección `accounts`) |
    | `balance_changes` | array\<object\> | No | Cambios en el balance de SOL (ver sección `balance_changes`) |
    | `pre_token_balances` | array\<object\> | No | Balances de tokens antes de la ejecución (ver sección `pre_token_balances`) |
    | `post_token_balances` | array\<object\> | No | Balances de tokens después de la ejecución (ver sección `post_token_balances`) |

    ---

    ## accounts

    Lista de cuentas involucradas en la transacción.

    | Campo | Tipo | Requerido | Descripción |
    |---|---|---|---|
    | `pubkey` | string | Sí | Clave pública de la cuenta (base58) |
    | `signer` | boolean | Sí | Indica si la cuenta firmó la transacción |
    | `writable` | boolean | Sí | Indica si la cuenta es escribible (puede modificarse) |

    ---

    ## balance_changes

    Cambios en el balance de SOL de las cuentas.

    | Campo | Tipo | Requerido | Descripción |
    |---|---|---|---|
    | `account` | string | Sí | Clave pública de la cuenta |
    | `before` | number | Sí | Balance antes de la transacción (lamports) |
    | `after` | number | Sí | Balance después de la transacción (lamports) |

    ---

    ## pre_token_balances

    Balances de tokens antes de ejecutar la transacción.

    | Campo | Tipo | Requerido | Descripción |
    |---|---|---|---|
    | `account_index` | integer | Sí | Índice dentro del arreglo `accounts` |
    | `mint` | string | Sí | Clave pública del mint del token |
    | `owner` | string | Sí | Clave pública del propietario de la cuenta de token |
    | `amount` | number | Sí | Cantidad de tokens (sin aplicar decimales) |
    | `decimals` | integer | Sí | Número de decimales del token |

    ---

    ## post_token_balances

    Balances de tokens después de ejecutar la transacción.

    | Campo | Tipo | Requerido | Descripción |
    |---|---|---|---|
    | `account_index` | integer | Sí | Índice dentro del arreglo `accounts` |
    | `mint` | string | Sí | Clave pública del mint del token |
    | `owner` | string | Sí | Clave pública del propietario de la cuenta de token |
    | `amount` | number | Sí | Cantidad de tokens (sin aplicar decimales) |
    | `decimals` | integer | Sí | Número de decimales del token |
    """)
    return


@app.cell
def _(duckdb, hf_hub_download, pl):
    file_path = hf_hub_download(
        repo_id="solarchive/solarchive",
        filename="txs/2021-06-20/000000000000.parquet",
        repo_type="dataset"
    )

    df = pl.read_parquet(file_path)

    duckdb.sql("DESCRIBE SELECT * FROM df").show()
    return (df,)


@app.cell
def _(duckdb):
    duckdb.sql("SELECT * FROM df LIMIT 1").show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Limpieza & Analisis
    """)
    return


@app.cell
def _(df):
    df.shape
    return


@app.cell
def _(df):
    df.null_count()
    return


@app.cell
def _(df):
    print(df['log_messages'].null_count())
    print(df['accounts'].null_count())
    print(df['balance_changes'].null_count())
    print(df['pre_token_balances'].null_count())
    print(df['post_token_balances'].null_count())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Division de Datos de Entrenamiento y Prueba
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transformacion de Variables
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
