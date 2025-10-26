import sqlite3
import pandas as pd
import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceManager:
    """
    Manages connections to various data sources including databases and Excel files.
    """
    
    def __init__(self):
        self.connections = {}
        self.schemas = {}
        self.config_file = "data_sources.json"
        self.load_config()
    
    def load_config(self):
        """Load data source configurations from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
                self.config = {"data_sources": {}}
        else:
            self.config = {"data_sources": {}}
    
    def save_config(self):
        """Save data source configurations to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save config: {e}")
    
    def add_database_source(self, name: str, db_type: str, connection_string: str, description: str = ""):
        """
        Add a database data source.
        
        Args:
            name: Unique name for the data source
            db_type: Type of database (sqlite, postgresql, mysql, etc.)
            connection_string: Database connection string
            description: Optional description
        """
        self.config["data_sources"][name] = {
            "type": "database",
            "db_type": db_type,
            "connection_string": connection_string,
            "description": description,
            "active": True
        }
        self.save_config()
        logger.info(f"Added database source: {name}")
    
    def add_excel_source(self, name: str, file_path: str, sheet_name: str = None, description: str = ""):
        """
        Add an Excel file data source.
        
        Args:
            name: Unique name for the data source
            file_path: Path to Excel file
            sheet_name: Specific sheet name (None for all sheets)
            description: Optional description
        """
        self.config["data_sources"][name] = {
            "type": "excel",
            "file_path": file_path,
            "sheet_name": sheet_name,
            "description": description,
            "active": True
        }
        self.save_config()
        logger.info(f"Added Excel source: {name}")
    
    def get_connection(self, source_name: str):
        """Get connection to a data source."""
        if source_name not in self.config["data_sources"]:
            raise ValueError(f"Data source '{source_name}' not found")
        
        source_config = self.config["data_sources"][source_name]
        
        if source_config["type"] == "database":
            return self._get_database_connection(source_config)
        elif source_config["type"] == "excel":
            return self._get_excel_connection(source_config)
        else:
            raise ValueError(f"Unsupported data source type: {source_config['type']}")
    
    def _get_database_connection(self, config: Dict):
        """Get database connection based on type."""
        db_type = config["db_type"].lower()
        connection_string = config["connection_string"]
        
        if db_type == "sqlite":
            return sqlite3.connect(connection_string)
        elif db_type == "postgresql":
            try:
                import psycopg2
                return psycopg2.connect(connection_string)
            except ImportError:
                raise ImportError("psycopg2 required for PostgreSQL connections")
        elif db_type == "mysql":
            try:
                import mysql.connector
                return mysql.connector.connect(connection_string)
            except ImportError:
                raise ImportError("mysql-connector-python required for MySQL connections")
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _get_excel_connection(self, config: Dict):
        """Convert Excel file to SQLite for querying."""
        file_path = config["file_path"]
        sheet_name = config.get("sheet_name")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        # Create temporary SQLite database
        temp_db_path = f"temp_{Path(file_path).stem}.db"
        
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                # Clean column names for SQL compatibility
                df.columns = [self._clean_column_name(col) for col in df.columns]
                df.to_sql(sheet_name, sqlite3.connect(temp_db_path), index=False, if_exists='replace')
            else:
                # Read all sheets
                excel_file = pd.ExcelFile(file_path)
                conn = sqlite3.connect(temp_db_path)
                
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    df.columns = [self._clean_column_name(col) for col in df.columns]
                    df.to_sql(sheet, conn, index=False, if_exists='replace')
                
                conn.close()
            
            return sqlite3.connect(temp_db_path)
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise
    
    def _clean_column_name(self, col_name: str) -> str:
        """Clean column names for SQL compatibility."""
        # Remove special characters and replace spaces with underscores
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name))
        # Ensure it doesn't start with a number
        if cleaned[0].isdigit():
            cleaned = f"col_{cleaned}"
        return cleaned
    
    def get_schema(self, source_name: str) -> str:
        """Get schema information for a data source."""
        if source_name in self.schemas:
            return self.schemas[source_name]
        
        source_config = self.config["data_sources"][source_name]
        
        if source_config["type"] == "database":
            schema = self._get_database_schema(source_name)
        elif source_config["type"] == "excel":
            schema = self._get_excel_schema(source_name)
        else:
            raise ValueError(f"Unsupported data source type: {source_config['type']}")
        
        self.schemas[source_name] = schema
        return schema
    
    def _get_database_schema(self, source_name: str) -> str:
        """Get schema from database."""
        conn = self.get_connection(source_name)
        cursor = conn.cursor()
        
        try:
            source_config = self.config["data_sources"][source_name]
            db_type = source_config["db_type"].lower()
            
            if db_type == "sqlite":
                return self._get_sqlite_schema(cursor)
            elif db_type == "postgresql":
                return self._get_postgresql_schema(cursor)
            elif db_type == "mysql":
                return self._get_mysql_schema(cursor)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
                
        finally:
            conn.close()
    
    def _get_sqlite_schema(self, cursor) -> str:
        """Get SQLite schema."""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        schema_parts = []
        for table_tuple in tables:
            table_name = table_tuple[0]
            schema_parts.append(f"Table: {table_name}")
            
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                nullable = "NOT NULL" if col[3] else "NULL"
                schema_parts.append(f"  - {col_name} ({col_type}, {nullable})")
            
            schema_parts.append("")
        
        return "\n".join(schema_parts).strip()
    
    def _get_postgresql_schema(self, cursor) -> str:
        """Get PostgreSQL schema."""
        cursor.execute("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
        columns = cursor.fetchall()
        
        schema_parts = []
        current_table = None
        
        for table_name, col_name, data_type, is_nullable in columns:
            if table_name != current_table:
                if current_table:
                    schema_parts.append("")
                schema_parts.append(f"Table: {table_name}")
                current_table = table_name
            
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            schema_parts.append(f"  - {col_name} ({data_type}, {nullable})")
        
        return "\n".join(schema_parts).strip()
    
    def _get_mysql_schema(self, cursor) -> str:
        """Get MySQL schema."""
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        schema_parts = []
        for table_tuple in tables:
            table_name = table_tuple[0]
            schema_parts.append(f"Table: {table_name}")
            
            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                schema_parts.append(f"  - {col_name} ({col_type}, {nullable})")
            
            schema_parts.append("")
        
        return "\n".join(schema_parts).strip()
    
    def _get_excel_schema(self, source_name: str) -> str:
        """Get schema from Excel file."""
        conn = self.get_connection(source_name)
        cursor = conn.cursor()
        
        try:
            return self._get_sqlite_schema(cursor)
        finally:
            conn.close()
    
    def list_sources(self) -> List[Dict]:
        """List all configured data sources."""
        sources = []
        for name, config in self.config["data_sources"].items():
            sources.append({
                "name": name,
                "type": config["type"],
                "description": config.get("description", ""),
                "active": config.get("active", True)
            })
        return sources
    
    def remove_source(self, name: str):
        """Remove a data source."""
        if name in self.config["data_sources"]:
            del self.config["data_sources"][name]
            self.save_config()
            logger.info(f"Removed data source: {name}")
        else:
            raise ValueError(f"Data source '{name}' not found")
    
    def set_active_source(self, name: str):
        """Set the active data source."""
        if name not in self.config["data_sources"]:
            raise ValueError(f"Data source '{name}' not found")
        
        # Deactivate all sources
        for source_config in self.config["data_sources"].values():
            source_config["active"] = False
        
        # Activate the selected source
        self.config["data_sources"][name]["active"] = True
        self.save_config()
        logger.info(f"Set active data source: {name}")
    
    def get_active_source(self) -> Optional[str]:
        """Get the currently active data source."""
        for name, config in self.config["data_sources"].items():
            if config.get("active", False):
                return name
        return None

# Global instance
data_manager = DataSourceManager()

