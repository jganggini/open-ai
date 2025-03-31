from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import oracledb, os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carga .env
load_dotenv("/opt/airflow/data/.env")

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def extract_data(**kwargs):
    """Extrae datos desde PostgreSQL y guarda records y cols en XCom."""
    try:
        print("Iniciando conexión a PostgreSQL...")
        pg_hook = PostgresHook(
            postgres_conn_id="openwebui_postgres",
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=os.getenv("POSTGRES_PORT", 5432),
            database=os.getenv("POSTGRES_DB", "openwebui"),
            user=os.getenv("POSTGRES_USER", "openwebui"),
            password=os.getenv("POSTGRES_PASSWORD", "securepass")
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        print("Conexión a PostgreSQL exitosa. Ejecutando consulta...")
        cursor.execute('SELECT * FROM "user"')
        records = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        print(f"Consulta ejecutada. Registros obtenidos: {len(records)}")
        print(f"Columnas obtenidas: {cols}")
        cursor.close()
        conn.close()
        print("Conexión a PostgreSQL cerrada.")
        
        # Guardar datos en XCom
        ti = kwargs['ti']
        ti.xcom_push(key='records', value=records)
        ti.xcom_push(key='cols', value=cols)
        # Además, retorna los datos para que estén disponibles al testear cada tarea de forma aislada
        return {'records': records, 'cols': cols}
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        raise

def transform_data(**kwargs):
    """Transforma los datos si es necesario."""
    try:
        ti = kwargs['ti']
        data = ti.xcom_pull(task_ids='extract_data')
        if not data:
            print("No se encontraron datos en XCom, ejecutando extract_data directamente...")
            data = extract_data(**kwargs)
        records = data.get('records', [])
        print("Iniciando transformación de datos...")
        print(f"Datos transformados: {len(records)} registros.")
    except Exception as e:
        print(f"Error al transformar los datos: {e}")
        raise

def load_data(**kwargs):
    """Carga los datos en Oracle."""
    try:
        print("Iniciando conexión a Oracle Autonomous Database...")
        ti = kwargs['ti']
        data = ti.xcom_pull(task_ids='extract_data')
        if not data:
            print("No se encontraron datos en XCom, ejecutando extract_data directamente...")
            data = extract_data(**kwargs)
        records = data.get('records', [])
        cols = data.get('cols', [])
        
        if not cols:
            raise ValueError("La lista de columnas 'cols' está vacía, se requiere ejecutar 'extract_data' correctamente.")
        
        conn = oracledb.connect(
            user            = os.getenv('CON_ADB_ADM_USER_NAME'),
            password        = os.getenv('CON_ADB_ADM_PASSWORD'),
            dsn             = os.getenv('CON_ADB_ADM_SERVICE_NAME'),
            config_dir      = os.getenv('CON_ADB_WALLET_LOCATION'),
            wallet_location = os.getenv('CON_ADB_WALLET_LOCATION'),
            wallet_password = os.getenv('CON_ADB_WALLET_PASSWORD')
        )
        cur = conn.cursor()
        print("Conexión a Oracle exitosa. Verificando si la tabla existe...")
        
        schema_name = os.getenv("ORACLE_SCHEMA_NAME", "ADMIN")
        table_name = "USER"
        cur.execute(f"""
            SELECT COUNT(*) 
            FROM all_tables 
            WHERE table_name = '{table_name}' AND owner = '{schema_name}'
        """)
        table_exists = cur.fetchone()[0] > 0
        
        if not table_exists:
            print(f"La tabla {schema_name}.{table_name} no existe. Creándola...")
            columns_definition = ", ".join([f'"{col}" VARCHAR2(4000)' for col in cols])
            create_table_sql = f'CREATE TABLE "{schema_name}"."{table_name}" ({columns_definition})'
            print(f"query: {create_table_sql}")
            cur.execute(create_table_sql)
            print(f"Tabla {schema_name}.{table_name} creada exitosamente.")
        else:
            print(f"Truncando la tabla {schema_name}.{table_name}...")
            cur.execute(f'TRUNCATE TABLE "{schema_name}"."{table_name}"')
            print(f"Tabla {schema_name}.{table_name} truncada con éxito.")
        
        print("Preparando inserción de datos...")
        cols_list = ", ".join(f'"{col}"' for col in cols)
        placeholders = ", ".join(f":{i+1}" for i in range(len(cols)))
        insert_sql = f'''
            INSERT INTO "{schema_name}"."{table_name}"({cols_list}) VALUES({placeholders})
        '''
        cur.executemany(insert_sql, records)
        conn.commit()
        print("Datos insertados correctamente en Oracle.")
        cur.close()
        conn.close()
        print("Conexión a Oracle cerrada.")
    except Exception as e:
        print(f"Error al conectar o insertar en Oracle: {e}")
        raise

with DAG(
    dag_id="postgres_openwebui_to_adb",
    default_args=DEFAULT_ARGS,
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False
) as dag:
    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data
    )

    extract_task >> transform_task >> load_task