# Exploración de transacciones de Solana

Proyecto de la materia de Big Data. La primera etapa consiste en entender los
datos antes de decidir la limpieza, las transformaciones y los modelos.

El análisis está en `notebooks/EDA.py`, un notebook de Marimo con operaciones
en Polars y tres gráficos de Matplotlib. `main.py` es el archivo inicial del
proyecto y no ejecuta el EDA.

## Ejecutar

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.14, según
`.python-version`. Desde la carpeta del repositorio:

```bash
uv sync --locked
uv run --locked marimo edit notebooks/EDA.py
```

La primera ejecución necesita internet para descargar el archivo de datos
(aproximadamente 298 MB). Se guarda en `data/huggingface/`, ignorado por Git.
Las ejecuciones posteriores reutilizan ese archivo. Para trabajar sin conexión
una vez instaladas las dependencias y descargados los datos:

```bash
HF_HUB_OFFLINE=1 uv run --locked --offline marimo edit notebooks/EDA.py
```

El Parquet contiene aproximadamente 1.15 GB sin comprimir. Deja varios GB de RAM
disponibles: el notebook carga el archivo completo y las operaciones necesitan
memoria adicional. Si el equipo no tiene suficiente memoria, el siguiente ajuste
será usar `pl.scan_parquet` para consultar solo las columnas necesarias.

## Muestra reproducible

- Fuente: [Solarchive en Hugging Face](https://huggingface.co/datasets/solarchive/solarchive),
  licencia CC BY 4.0; según su documentación, excluye transacciones de voto.
- Archivo: `txs/2021-06-20/000000000000.parquet`.
- Revisión fijada: `6588cad2832e62be03972ac80d69c6af11d631c8`.
- Una fila representa una transacción; el notebook comprueba firmas nulas y repetidas.

Es un único archivo. No asumimos que incluya todas las transacciones del día
ni que represente toda la actividad histórica de Solana. Los timestamps del
archivo no declaran zona horaria; no se realiza una conversión implícita.

## Qué revisa el notebook

1. Primeras filas, dimensiones y tipos reales.
2. Cobertura temporal y fechas nulas.
3. Nulos por columna, campos requeridos y repeticiones adicionales de firmas no nulas.
4. Listas nulas frente a listas vacías en cuentas, logs y balances.
5. Estados, frecuencias de comisiones, percentiles 90 y 99 y comparación por estado.
6. Una tabla derivada con columnas sencillas para continuar la exploración.
7. Relación entre estado y presencia de error; diez mensajes de error más frecuentes.
8. Número de cuentas y firmantes; nulos internos en `pubkey`, `signer` y `writable`.
9. Transacciones y porcentaje de fallos por hora.
10. Comisiones según número de firmantes, con explicación de firma y mediana.
11. Porcentaje de fallos según número de cuentas, con conclusiones en lenguaje sencillo.
12. Las seis comisiones diferentes: cuentas implicadas y mensajes de ejecución.
13. Comparación de errores entre transacciones con 6, 7 y 8 cuentas.
14. Primeras decisiones de limpieza y su justificación, sin modificar los datos.

Los estados se agrupan según sus valores reales (en esta muestra: `Success` y
`Fail`). El porcentaje por estado usa todas las filas; el porcentaje de cada
error usa todas las transacciones `Fail`, y el porcentaje de fallos por hora
usa todas las transacciones de esa hora. Los percentiles se calculan con
interpolación lineal. Las comisiones se expresan en lamports; 1 SOL equivale a
1,000,000,000 lamports.

Los tres gráficos muestran los diez errores más frecuentes, las diez comisiones
más frecuentes (o todas si hay menos de diez) y el volumen por hora. Las tablas
conservan los mensajes completos. Un código de error específico no se interpreta
sin conocer el programa que lo produjo.

Las estadísticas numéricas usan una copia convertida a punto flotante para
facilitar su descripción; no son cálculos contables exactos. El DataFrame
original y el archivo permanecen intactos. No se eliminan nulos, se imputan
valores ni se deduplican transacciones automáticamente. Los campos internos de
balances y logs todavía requieren revisión si se usan en análisis posteriores.

## Tabla derivada

`df_eda` permanece en memoria, con una fila por transacción y diez columnas:

| Columnas | Uso |
|---|---|
| `signature`, `block_slot`, `block_timestamp`, `status`, `err`, `fee` | Valores originales para trazabilidad y comparación. |
| `fee_sol` | Comisión dividida entre mil millones; aproximada por usar punto flotante. |
| `hora` | Fecha y hora truncadas a la hora, sin asignar zona horaria. |
| `n_cuentas` | Número de elementos de `accounts`; una lista nula conserva un conteo nulo. |
| `n_firmantes` | Número de indicadores `signer=True`; es nulo si la lista o algún indicador son desconocidos. |

Una lista vacía tiene cero elementos. Contar cuentas no equivale a contar personas.
No se exporta otro dataset ni se modifica `df`.

## Esquema frente a datos observados

El [esquema publicado de transacciones](https://huggingface.co/datasets/solarchive/solarchive/blob/main/schemas/transactions.json)
marca siete campos requeridos: `block_slot`, `block_hash`, `block_timestamp`,
`signature`, `index`, `fee` y `status`. Esto no indica importancia para modelos.
En esta muestra no tienen nulos.

El esquema enumera `Failed`, pero nuestro archivo usa `Fail`. Además,
`compute_units_consumed` está declarado numérico sin admitir explícitamente
nulos, aunque en este archivo todos sus valores son nulos. Estas diferencias se
documentan; no se usan para eliminar registros o modificar etiquetas.

## Hallazgos verificados en esta muestra

- 707,493 filas y 707,493 firmas distintas, sin firmas nulas.
- 647,933 transacciones con estado `Success` y 59,560 con estado `Fail`.
- Fechas entre `2021-06-20 00:00:03` y `2021-06-20 23:59:59`.
- Ninguna comisión nula o negativa.
- Comisión mínima, mediana y percentil 90: 5,000 lamports; percentil 99: 15,000;
  máxima: 35,000.
- 61 mensajes de error distintos. Las 59,560 transacciones `Fail` tienen mensaje;
  las 647,933 `Success` tienen `err` nulo. Esos nulos son esperados.
- Entre 3 y 32 cuentas y entre 1 y 6 firmantes por transacción. Sin nulos internos
  en `accounts.pubkey`, `accounts.signer` ni `accounts.writable`.
- La hora de mayor volumen es `2021-06-20 10:00`: 35,953 transacciones,
  con 4,136 fallidas (11.50 %).
- `compute_units_consumed` es nulo en todas las filas: esa columna no permite
  estudiar el consumo de cómputo. Algunos logs sí contienen consumos por programa,
  pero no se suman automáticamente porque las llamadas pueden estar anidadas.

Estos resultados corresponden únicamente al archivo y la revisión fijados arriba.

## Cómo interpretar las dos comparaciones

En 707,487 de las 707,493 transacciones, la comisión coincide con 5,000 lamports
por firmante. Una firma autoriza una operación y la red debe comprobarla:
el patrón es compatible con un cobro ligado a ese trabajo. Hay seis excepciones
que investigamos mediante sus cuentas y logs, sin eliminarlas ni asumir que sean errores.
La comisión es el costo de procesamiento, no la cantidad de dinero transferida.

La proporción de fallos no crece de forma constante con el número de cuentas:
con seis cuentas es 0.05 %, con siete es 16.99 % y con ocho baja a 0.62 %.
Una posible explicación es que los grupos contengan distintos tipos de operaciones.
Todavía no lo hemos comprobado. No podemos concluir que añadir cuentas cause fallos.

El notebook separa **qué encontramos**, **cómo podría explicarse** y
**qué falta comprobar**. Las tablas muestran el tamaño de los grupos para no
dar el mismo peso a un grupo de una transacción que a uno de miles.

## Investigación de las excepciones y los errores

Las seis excepciones tienen una cuenta firmante. Cinco pagaron 35,000 lamports
y una pagó 10,000; cuatro fueron exitosas y dos fallidas. Todas incluyen la dirección
del verificador Secp256k1. Los cinco casos de 35,000 contienen `VerifySignatures`
en sus logs; los dos fallidos también contienen `AlreadyExists`.

Esto es compatible con verificaciones adicionales de firmas que nuestro conteo
de cuentas firmantes no recoge. La presencia del programa no prueba por sí sola
que se ejecutara ni permite reconstruir exactamente cada comisión histórica.
El archivo carece de las instrucciones completas necesarias para confirmarlo.
Referencias: [programas de verificación](https://solana.com/docs/core/programs/precompiles)
y [comisiones](https://solana.com/docs/core/fees/fee-structure).

Los errores se concentran de forma distinta en los tres grupos:

| Cuentas | Transacciones | Fallidas | Mensaje más frecuente entre las fallidas | Casos | % de las fallidas del grupo |
|---|---:|---:|---|---:|---:|
| 6 | 274,819 | 139 | Instruction 0: custom program error: 0xaa | 124 | 89.21 % |
| 7 | 130,709 | 22,209 | Instruction 0: custom program error: 0x29 | 18,362 | 82.68 % |
| 8 | 1,440 | 9 | Instruction 0: custom program error: 0x17 | 4 | 44.44 % |

Son mensajes agrupados, no causas confirmadas. El significado de cada código
depende del programa que lo emitió. El grupo de ocho cuentas tiene solo nueve
fallos: sus porcentajes pueden cambiar bastante con pocos casos adicionales.

Las decisiones iniciales son conservar `err` nulo cuando la operación fue exitosa,
conservar las seis excepciones y no deduplicar firmas que ya son únicas. La columna
de cómputo vacía se mantiene en el original, pero no se usa como medida de consumo.
Antes de usar balances o combinar fechas, revisaremos sus campos internos y las
diferencias de etiquetas. No se ha aplicado ninguna eliminación o imputación.

## Validar y exportar

```bash
uv run --locked marimo check --strict notebooks/EDA.py
mkdir -p output
HF_HUB_OFFLINE=1 uv run --locked --offline marimo export html notebooks/EDA.py -o output/EDA.html --force
```

La exportación ejecuta el notebook completo y genera un HTML con sus resultados.
`output/` está ignorado por Git. El comando sin conexión requiere haber
descargado la muestra primero.

Se verificó que `df_eda` conserva las 707,493 filas, las firmas y las comisiones
originales; los totales por hora, error y comisión se contrastaron con DuckDB
leyendo el Parquet. También se comprobó la celda de derivación con listas nulas,
vacías y elementos o indicadores de firma desconocidos, y se inspeccionaron los
tres gráficos renderizados.
La selección de las seis excepciones y los conteos por error de los grupos de
6, 7 y 8 cuentas también se contrastaron con DuckDB. Se verificaron las pistas
descritas en los logs y los denominadores de los porcentajes de cada grupo.

## Próximos pasos

Definir una pregunta concreta y decidir qué otras fechas necesitamos para
comprobar si los patrones se repiten. La división entrenamiento/prueba y las transformaciones
que aprenden de los datos se definirán cuando exista un objetivo predictivo.

Esta etapa se desarrolla en `eda-sebastian`, creada desde `Solano`.
