import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    from pathlib import Path
    from textwrap import fill

    import marimo as mo
    import matplotlib.pyplot as plt
    from huggingface_hub import hf_hub_download
    import polars as pl

    return Path, fill, hf_hub_download, mo, pl, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exploración inicial de transacciones de Solana

    Queremos conocer la estructura, la calidad y las distribuciones de una muestra
    antes de decidir qué limpiar o qué modelos aplicar.

    Fuente: [Solarchive](https://huggingface.co/datasets/solarchive/solarchive).
    Según la fuente, estas transacciones excluyen los votos de validadores.
    Una fila representa una transacción; comprobaremos la unicidad de `signature`.
    Analizamos **un archivo**, no toda Solana ni necesariamente un día completo.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Solana Transaction Schema

    Referencia de los campos del dataset público de BigQuery (sin transacciones de voto).
    Los campos marcados como requeridos describen la referencia, no garantizan que
    la muestra no tenga nulos. Más abajo consultamos los tipos y valores reales.

    ## Campos principales

    | Campo | Tipo | Requerido | Descripción |
    |---|---|---|---|
    | `block_slot` | integer | Sí | Número de slot del bloque que contiene la transacción |
    | `block_hash` | string | Sí | Hash del bloque que contiene la transacción |
    | `block_timestamp` | timestamp | Sí | Marca de tiempo en que se produjo el bloque |
    | `recent_block_hash` | string | No | Blockhash reciente usado por la transacción |
    | `signature` | string | Sí | Firma única de la transacción (codificada en base58) |
    | `index` | integer | Sí | Índice de la transacción dentro del bloque |
    | `fee` | number | Sí | Comisión pagada en lamports (1 SOL = 1,000,000,000 lamports) |
    | `status` | string (`Success` \| `Fail` en esta muestra) | Sí | Estado de ejecución de la transacción |
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


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. Carga de la muestra
    """)
    return


@app.cell
def _(Path, hf_hub_download, pl):
    revision = "6588cad2832e62be03972ac80d69c6af11d631c8"
    archivo = "txs/2021-06-20/000000000000.parquet"
    file_path = hf_hub_download(
        repo_id="solarchive/solarchive",
        filename=archivo,
        revision=revision,
        repo_type="dataset",
        cache_dir=Path(__file__).resolve().parents[1] / "data" / "huggingface",
    )
    df = pl.read_parquet(file_path)
    return (df,)


@app.cell
def _(df):
    df.head(5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. Dimensiones, tipos y fechas
    """)
    return


@app.cell
def _(df, mo):
    mo.md(f"""
    **Filas:** {df.height:,} · **Columnas:** {df.width}
    """)
    return


@app.cell
def _(df, pl):
    pl.DataFrame({
        "columna": df.columns,
        "tipo": [str(tipo) for tipo in df.dtypes],
    })
    return


@app.cell
def _(df, pl):
    df.select(
        pl.col("block_timestamp").min().alias("fecha_minima"),
        pl.col("block_timestamp").max().alias("fecha_maxima"),
        pl.col("block_timestamp").null_count().alias("fechas_nulas"),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3. Nulos y firmas repetidas
    """)
    return


@app.cell
def _(df, pl):
    nulos = pl.DataFrame({
        "columna": df.columns,
        "nulos": df.null_count().row(0),
    }).with_columns(
        (pl.col("nulos") / df.height * 100).round(2).alias("porcentaje")
    ).sort("nulos", descending=True)
    nulos
    return


@app.cell
def _(df, pl):
    requeridos = [
        "block_slot", "block_hash", "block_timestamp", "signature",
        "index", "fee", "status",
    ]
    df.select(pl.col(requeridos).null_count())
    return


@app.cell
def _(df, pl):
    firmas = df.select(
        pl.col("signature").null_count().alias("firmas_nulas"),
        pl.col("signature").drop_nulls().n_unique().alias("firmas_unicas"),
        (
            pl.col("signature").drop_nulls().len()
            - pl.col("signature").drop_nulls().n_unique()
        ).alias("repeticiones_adicionales"),
    )
    firmas
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 4. Columnas con listas
    """)
    return


@app.cell
def _(df, pl):
    listas = pl.DataFrame([
        {
            "columna": columna,
            "listas_nulas": df[columna].null_count(),
            "listas_vacias": (df[columna].list.len() == 0).sum(),
        }
        for columna in [
            "log_messages", "accounts", "balance_changes",
            "pre_token_balances", "post_token_balances",
        ]
    ])
    listas
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. Estados y comisiones
    Las comisiones están en lamports: **1 SOL = 1,000,000,000 lamports**.
    """)
    return


@app.cell
def _(df, pl):
    estados = df.group_by("status").len(name="transacciones").with_columns(
        (pl.col("transacciones") / df.height * 100).round(2).alias("porcentaje")
    ).sort("transacciones", descending=True)
    estados
    return


@app.cell
def _(df, pl):
    df.select("fee", "compute_units_consumed").cast(pl.Float64).describe()
    return


@app.cell
def _(df, pl):
    df.group_by("status").agg(
        pl.len().alias("transacciones"),
        pl.col("fee").count().alias("comisiones_no_nulas"),
        pl.col("fee").cast(pl.Float64).mean().alias("comision_media_lamports"),
        pl.col("fee").cast(pl.Float64).median().alias("comision_mediana_lamports"),
    ).sort("status")
    return


@app.cell
def _(df, pl):
    df.select(pl.col("fee").cast(pl.Float64)).select(
        pl.col("fee").min().alias("minimo"),
        pl.col("fee").median().alias("mediana"),
        pl.col("fee").quantile(0.90, interpolation="linear").alias("p90"),
        pl.col("fee").quantile(0.99, interpolation="linear").alias("p99"),
        pl.col("fee").max().alias("maximo"),
    )
    return


@app.cell
def _(df):
    frecuencias_comision = df.group_by("fee").len(name="transacciones").sort(
        ["transacciones", "fee"], descending=[True, False], nulls_last=True
    )
    frecuencias_comision
    return (frecuencias_comision,)


@app.cell
def _(frecuencias_comision, plt):
    _top = frecuencias_comision.head(10)
    fig_comisiones, _ax = plt.subplots(figsize=(9, 4), layout="constrained")
    _ax.bar(
        ["Nula" if valor is None else f"{valor:,.0f}" for valor in _top["fee"]],
        _top["transacciones"].to_list(),
        color="#236B8E",
    )
    _ax.set(title="Comisiones más frecuentes",
            xlabel="Comisión en lamports", ylabel="Transacciones")
    _ax.tick_params(axis="x", labelrotation=45)
    plt.close(fig_comisiones)
    fig_comisiones
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 6. Tabla derivada para explorar
    """)
    return


@app.cell
def _(df, pl):
    df_eda = df.select(
        "signature", "block_slot", "block_timestamp", "status", "err", "fee",
        (pl.col("fee").cast(pl.Float64) / 1_000_000_000).alias("fee_sol"),
        pl.col("block_timestamp").dt.truncate("1h").alias("hora"),
        pl.col("accounts").list.len().alias("n_cuentas"),
        pl.when(
            pl.col("accounts").is_not_null()
            & ~pl.col("accounts").list.eval(
                pl.element().struct.field("signer").is_null()
            ).list.any()
        ).then(
            pl.col("accounts").list.eval(
                pl.element().struct.field("signer").cast(pl.UInt32)
            ).list.sum()
        ).otherwise(None).alias("n_firmantes"),
    )
    df_eda.head(5)
    return (df_eda,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 7. Errores de ejecución
    """)
    return


@app.cell
def _(df_eda, pl):
    df_eda.with_columns(
        pl.when(pl.col("err").is_null()).then(pl.lit("Nulo"))
        .when(pl.col("err") == "").then(pl.lit("Vacío"))
        .otherwise(pl.lit("Informado")).alias("mensaje_error")
    ).group_by("status", "mensaje_error").len(name="transacciones").sort(
        "status", "mensaje_error"
    )
    return


@app.cell
def _(df_eda, pl):
    fallidas = df_eda.filter(pl.col("status") == "Fail")
    errores = fallidas.group_by("err").len(name="transacciones").with_columns(
        (pl.col("transacciones") / fallidas.height * 100)
        .round(2).alias("porcentaje_de_fallidas")
    ).sort(["transacciones", "err"], descending=[True, False], nulls_last=True)
    errores.head(10)
    return (errores,)


@app.cell
def _(errores, fill, plt):
    _top = errores.head(10).reverse()
    fig_errores, _ax = plt.subplots(figsize=(12, 8), layout="constrained")
    _etiquetas = [
        fill("Nulo" if mensaje is None else mensaje or "Vacío", width=55)
        for mensaje in _top["err"]
    ]
    _ax.barh(_etiquetas, _top["transacciones"].to_list(), color="#B45B38")
    _ax.set(title="Mensajes de error más frecuentes",
            xlabel="Transacciones fallidas", ylabel="Mensaje original")
    _ax.tick_params(axis="y", labelsize=9)
    plt.close(fig_errores)
    fig_errores
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 8. Cuentas y firmantes
    """)
    return


@app.cell
def _(df, pl):
    df.select([
        pl.col("accounts").list.eval(
            pl.element().struct.field(campo).is_null()
        ).list.sum().sum().alias(f"nulos_{campo}")
        for campo in ["pubkey", "signer", "writable"]
    ])
    return


@app.cell
def _(df_eda):
    df_eda.select("n_cuentas", "n_firmantes").describe()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 9. Actividad por hora
    """)
    return


@app.cell
def _(df_eda, pl):
    actividad_hora = df_eda.group_by("hora").agg(
        pl.len().alias("transacciones"),
        (pl.col("status") == "Fail").sum().alias("fallidas"),
    ).with_columns(
        (pl.col("fallidas") / pl.col("transacciones") * 100)
        .round(2).alias("porcentaje_fallidas")
    ).sort("hora", nulls_last=True)
    actividad_hora
    return (actividad_hora,)


@app.cell
def _(actividad_hora, plt):
    _horas = actividad_hora.drop_nulls("hora")
    fig_horas, _ax = plt.subplots(figsize=(10, 4), layout="constrained")
    _ax.plot(_horas["hora"].to_list(), _horas["transacciones"].to_list(),
             marker="o", color="#28785D")
    _ax.set(title="Transacciones por hora en la muestra",
            xlabel="Fecha y hora del archivo", ylabel="Transacciones")
    _ax.tick_params(axis="x", labelrotation=45)
    _ax.set_ylim(bottom=0)
    plt.close(fig_horas)
    fig_horas
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 10. ¿Por qué cambia la comisión entre transacciones?

    Una **firma digital** sirve para autorizar una operación. Un **firmante** es
    una cuenta que aporta esa autorización; no necesariamente una persona distinta.
    La red tiene que comprobar las firmas, y una parte de la comisión está
    relacionada con ese trabajo. Por eso tiene sentido comparar comisión y firmantes.

    La **mediana** es el valor que queda en medio al ordenar las comisiones.
    Nos ayuda a describir una comisión habitual sin que unos pocos valores altos
    cambien mucho el resultado.
    [Referencia: comisiones de Solana](https://solana.com/docs/core/fees/fee-structure).
    """)
    return


@app.cell
def _(df_eda, pl):
    comisiones_firmantes = df_eda.group_by("n_firmantes").agg(
        pl.len().alias("transacciones"),
        pl.col("fee").count().alias("comisiones_no_nulas"),
        pl.col("fee").min().alias("comision_minima_lamports"),
        pl.col("fee").cast(pl.Float64).median().alias("comision_mediana_lamports"),
        pl.col("fee").max().alias("comision_maxima_lamports"),
    ).sort("n_firmantes", nulls_last=True)
    comisiones_firmantes
    return


@app.cell(hide_code=True)
def _(df_eda, mo, pl):
    _comparables = df_eda.drop_nulls(["fee", "n_firmantes"])
    _coinciden = _comparables.filter(
        pl.col("fee") == pl.col("n_firmantes") * 5000
    ).height
    _distintas = _comparables.height - _coinciden
    mo.md(f"""
    **Qué encontramos:** en {_coinciden:,} de {_comparables.height:,} transacciones
    con ambos datos conocidos, la comisión coincide con **5,000 lamports por firmante**.
    Por ejemplo, esa relación equivale a 5,000 para uno y 10,000 para dos.

    Esto describe nuestra muestra de 2021. La documentación actual ayuda a entender
    el mecanismo, pero no demuestra por sí sola la causa de cada comisión histórica.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 11. ¿Las transacciones con más cuentas fallan más?

    Una **cuenta** es un registro que la operación puede consultar o modificar:
    puede guardar saldo, datos de un token u otra información. Una operación
    puede necesitar varias cuentas y solo algunas tienen que firmar.
    Más cuentas no significa necesariamente más personas.
    [Referencia: cuentas de Solana](https://solana.com/docs/core/accounts).

    Para comparar grupos usamos el **porcentaje de fallos**.
    """)
    return


@app.cell
def _(df_eda, pl):
    fallos_cuentas = df_eda.group_by("n_cuentas").agg(
        pl.len().alias("transacciones"),
        (pl.col("status") == "Fail").sum().alias("fallidas"),
    ).with_columns(
        (pl.col("fallidas") / pl.col("transacciones") * 100)
        .round(2).alias("porcentaje_fallidas")
    ).sort("n_cuentas", nulls_last=True)
    fallos_cuentas
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    **Qué encontramos en este archivo:** con 6 cuentas falla alrededor del 0.05 %
    de las transacciones; con 7, el 16.99 %. Sin embargo, con 8 cuentas baja
    al 0.62 %. Por tanto, no aparece una regla sencilla de «más cuentas, más fallos».
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 12. Revisar las seis comisiones diferentes

    Buscamos las operaciones cuya comisión no coincide con 5,000 lamports por
    cuenta firmante. Es una comparación con el patrón observado, no una regla
    para decidir que una transacción está mal.

    Añadimos sus cuentas y **logs**, que son mensajes registrados mientras se
    ejecuta la operación. La columna `incluye_secp256k1` indica si aparece la
    dirección de un programa especializado en comprobar firmas adicionales.
    """)
    return


@app.cell
def _(df, df_eda, pl):
    excepciones_comision = df_eda.filter(
        pl.col("fee") != pl.col("n_firmantes") * 5000
    ).join(
        df.select("signature", "accounts", "log_messages"),
        on="signature", how="left", validate="1:1",
    ).with_columns(
        (pl.col("fee") - pl.col("n_firmantes") * 5000).alias("diferencia_lamports"),
        pl.col("accounts").list.eval(
            pl.element().struct.field("pubkey")
            == "KeccakSecp256k11111111111111111111111111111"
        ).list.any().alias("incluye_secp256k1"),
    ).sort("signature")
    excepciones_comision.select(
        "signature", "fee", "diferencia_lamports", "n_firmantes",
        "n_cuentas", "status", "err", "incluye_secp256k1",
    )
    return (excepciones_comision,)


@app.cell
def _(excepciones_comision):
    excepciones_comision.select("signature", "log_messages")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    **Qué encontramos:** las seis operaciones tienen una cuenta firmante.
    Cinco pagaron 35,000 lamports y una pagó 10,000. Cuatro terminaron bien y
    dos fallaron. Todas incluyen la dirección del verificador de firmas Secp256k1.
    En los cinco casos de 35,000, los logs mencionan `VerifySignatures`. En los dos fallidos también aparece `AlreadyExists`

    **Cómo podría explicarse:** una cuenta puede autorizar la transacción y,
    además, la operación puede pedir comprobar otras firmas. Esas comprobaciones
    también pueden generar comisiones. Por eso contar cuentas firmantes puede
    quedarse corto para explicar el costo total.

    Fuentes: [verificador Secp256k1](https://solana.com/docs/core/programs/precompiles)
    y [cálculo de comisiones](https://solana.com/docs/core/fees/fee-structure).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 13. ¿Qué errores aparecen con 6, 7 y 8 cuentas?
    """)
    return


@app.cell
def _(df_eda, pl):
    grupos_cuentas = df_eda.filter(pl.col("n_cuentas").is_in([6, 7, 8]))
    resumen_grupos = grupos_cuentas.group_by("n_cuentas").agg(
        pl.len().alias("transacciones"),
        (pl.col("status") == "Fail").sum().alias("fallidas"),
    ).with_columns(
        (pl.col("fallidas") / pl.col("transacciones") * 100)
        .round(2).alias("porcentaje_fallidas"),
    ).sort("n_cuentas")
    resumen_grupos
    return (grupos_cuentas,)


@app.cell
def _(grupos_cuentas, pl):
    errores_grupos = grupos_cuentas.filter(pl.col("status") == "Fail").group_by(
        "n_cuentas", "err"
    ).len(name="transacciones").with_columns(
        (pl.col("transacciones") / pl.col("transacciones").sum().over("n_cuentas") * 100)
        .round(2).alias("porcentaje_de_fallidas_del_grupo"),
    ).sort(["n_cuentas", "transacciones", "err"], descending=[False, True, False])
    errores_grupos
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    **Qué encontramos:** con 6 cuentas hay 139 fallos; 124 comparten el mensaje
    que termina en `0xaa` (89.21 % de sus fallos). Con 7 cuentas hay 22,209 fallos;
    18,362 comparten el mensaje que termina en `0x29` (82.68 %).
    Con 8 cuentas solo hay 9 fallos; el mensaje más frecuente termina en `0x17`
    y aparece 4 veces (44.44 %).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 14. Primeras decisiones de limpieza

    | Qué encontramos | Qué decidimos | Por qué |
    |---|---|---|
    | `err` nulo en transacciones exitosas | Conservar esas filas y esos nulos | No hubo un error que registrar. |
    | `compute_units_consumed` completamente nulo | Dejarlo en `df`, fuera de los análisis numéricos útiles | Falta información; rellenar con cero inventaría un consumo. |
    | Firmas únicas en esta muestra | No deduplicar | No encontramos firmas repetidas que justifiquen esa operación. |
    | Estado `Fail` distinto de `Failed` en el esquema | Conservar el valor original | Primero documentamos la diferencia antes de combinar otras fuentes. |
    | Campos internos de balances todavía sin revisar | No usarlos aún para sacar conclusiones | Necesitamos conocer sus nulos, unidades y relaciones. |
    """)
    return


if __name__ == "__main__":
    app.run()
