# RECONNAISSANCE.md: Meltano Ground Truth

## Target: [meltano/meltano](https://github.com/meltano/meltano)

### 1. Primary Data Ingestion Path
Meltano is an ELT orchestration platform. Data ingestion is primarily handled through **Singer Taps**. 
- **Mechanism**: Meltano invokes external Singer-compliant executables (`taps`) to extract data from various sources (databases, APIs).
- **Orchestration**: Managed by `src/meltano/core/runner/singer.py` and `src/meltano/core/plugin_invoker.py`.
- **Data Flow**: `Source -> Tap (stdout) -> Meltano -> Target (stdin) -> Destination`.

### 2. Critical Output Datasets/Endpoints
- **Target Destinations**: Databases (Snowflake, BigQuery, etc.) or files loaded via Singer **Targets**.
- **Internal Metadata**: Meltano uses a SQLite/PostgreSQL/MySQL database for job state, logging, and configuration (see `src/meltano/core/db.py`).
- **State Store**: Managed job states used for incremental syncs, stored in `src/meltano/core/state_store/`.

### 3. Blast Radius Analysis
The most critical module is **`meltano.core`**.
- **`project.py`**: A failure here prevents any Meltano command from executing (cannot resolve project context).
- **`plugin_invoker.py`**: A failure here breaks all extraction/loading capabilities.
- **`settings_service.py`**: Changes to this module affect how every plugin is configured and executed.

### 4. Logic Concentration vs. Distribution
- **Concentrated**: `src/meltano/core` contains the central logic for plugin management, environment management, and configuration.
- **Distributed**: The actual data transformation and extraction logic is distributed across **Singer Taps/Targets** (external plugins) and **dbt** (external transformation tool).

### 5. Git Velocity (Top 5 Coding Files - Last 90 Days)
1. `src/meltano/core/plugin/singer/tap.py`
2. `src/meltano/core/state_store/filesystem.py`
3. `src/meltano/core/plugin/settings_service.py`
4. `src/meltano/core/project.py`
5. `src/meltano/core/job/` (various files)

*Note: Infrastructure files like `uv.lock` and `pyproject.toml` also show extremely high velocity.*
