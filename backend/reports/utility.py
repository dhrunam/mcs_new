from django.conf import settings
from django.db import connections
from .models import OrganizationDatabase
from accounts import models as auth_models
from rest_framework import exceptions

def get_database_connection(org_id):
    """
    Fetch database credentials for the given org_id and create a dynamic database connection.
    """
    try:
        # Fetch database credentials from the OrganizationDatabase model
        org_db = OrganizationDatabase.objects.get(organisation=org_id)

        # Configure the database connection
        db_config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': org_db.db_name,
            'USER': org_db.db_user,
            'PASSWORD': org_db.db_password,
            'HOST': org_db.db_host,
            'PORT': org_db.db_port,
            'OPTIONS': {
                'MAX_CONNS': 10,
                'MIN_CONNS': 1,
                'options': f'-c timezone={settings.TIME_ZONE}' 
            },
            # 'ATOMIC_REQUESTS':False,
        }

        # Dynamically register the connection
        connection_name = f"org_{org_id}_db"
        if connection_name not in connections.databases:
            connections.databases[connection_name] = db_config

        return connection_name

    except OrganizationDatabase.DoesNotExist:
        raise ValueError(f"No database configuration found for org_id {org_id}")
    except Exception as e:
        raise RuntimeError(f"Error setting up database connection: {str(e)}")
    
def get_organization_id(request):
    org_id=3
    organnization = request.query_params.get('organnization')
    if organnization:
        org_id=organnization
    else:
        user_profile= auth_models.UserProfile.objects.filter(user=request.user.id).last()
        if user_profile:
            org_id=user_profile.organization.id

    if org_id:
       return org_id
    else:
         return exceptions.APIException(detail='Organizaqtion not found!')



import psycopg2
from psycopg2 import pool
from .models import OrganizationDatabase

class DatabaseConnectionManager:
    """
    Manages PostgreSQL database connections dynamically for different organizations.
    Uses connection pooling for efficiency.
    """

    _connection_pools = {}

  

    @staticmethod
    def get_connection(org_id):
        """
        Get a connection to the database for the given org_id.
        Creates a new connection pool if it doesn't exist.
        """
        try:
            # Check if a connection pool exists for this org_id
            if org_id not in DatabaseConnectionManager._connection_pools:
                # Fetch the database credentials from the OrganizationDatabase model
                org_db = OrganizationDatabase.objects.get(organisation=org_id)
                
                # Create a new connection pool
                DatabaseConnectionManager._connection_pools[org_id] = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    user=org_db.db_user,
                    password=org_db.db_password,
                    host=org_db.db_host,
                    port=org_db.db_port,
                    database=org_db.db_name
                )

            # Get a connection from the pool
        
            connection = DatabaseConnectionManager._connection_pools[org_id].getconn()

            # Set the timezone explicitly for the connection
            with connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE 'UTC';")

            return connection

        except OrganizationDatabase.DoesNotExist:
            raise ValueError(f"No database configuration found for org_id {org_id}")
        except Exception as e:
            raise RuntimeError(f"Error setting up database connection for org_id {org_id}: {str(e)}")

    @staticmethod
    def release_connection(org_id, connection):
        """
        Release the connection back to the pool for the given org_id.
        """
        if org_id in DatabaseConnectionManager._connection_pools:
            DatabaseConnectionManager._connection_pools[org_id].putconn(connection)

    @staticmethod
    def close_all_connections():
        """
        Close all connection pools.
        """
        for pool in DatabaseConnectionManager._connection_pools.values():
            pool.closeall()
   