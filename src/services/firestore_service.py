"""Google Cloud Firestore service integration."""
from typing import Optional, Dict, Any, List
from google.cloud import firestore
from datetime import datetime

from src.core import Config, get_logger, GoogleServicesError

logger = get_logger(__name__)


class FirestoreService:
    """Handles Firestore operations."""

    def __init__(self, config: Config):
        """Initialize Firestore service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.db = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Firestore client."""
        try:
            if not self.config.USE_FIRESTORE:
                logger.info("Firestore is disabled in config")
                return

            self.db = firestore.Client(
                project=self.config.GOOGLE_CLOUD_PROJECT,
                database=self.config.FIRESTORE_DATABASE
            )
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {str(e)}")
            self.db = None

    def save_document(self, collection: str, document_id: str, data: Dict[str, Any]):
        """Save a document to Firestore.

        Args:
            collection: Collection name
            document_id: Document ID
            data: Document data

        Raises:
            GoogleServicesError: If save fails
        """
        if not self.db:
            logger.warning("Firestore client not initialized, skipping save")
            return

        try:
            data["updated_at"] = datetime.utcnow()
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow()

            self.db.collection(collection).document(document_id).set(data)
            logger.info(f"Saved document {document_id} to collection {collection}")
        except Exception as e:
            logger.error(f"Firestore save failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to save document to Firestore: {str(e)}",
                service="Firestore",
            )

    def get_document(
        self,
        collection: str,
        document_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore.

        Args:
            collection: Collection name
            document_id: Document ID

        Returns:
            Document data or None
        """
        if not self.db:
            return None

        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Firestore get failed: {str(e)}")
            return None

    def query_documents(
        self,
        collection: str,
        filters: List[tuple],
    ) -> List[Dict[str, Any]]:
        """Query documents in a collection.

        Args:
            collection: Collection name
            filters: List of (field, op, value) tuples

        Returns:
            List of matching documents
        """
        if not self.db:
            return []

        try:
            query = self.db.collection(collection)
            for field, op, value in filters:
                query = query.where(field, op, value)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Firestore query failed: {str(e)}")
            return []

    def delete_document(self, collection: str, document_id: str):
        """Delete a document from Firestore.

        Args:
            collection: Collection name
            document_id: Document ID
        """
        if not self.db:
            return

        try:
            self.db.collection(collection).document(document_id).delete()
            logger.info(f"Deleted document {document_id} from collection {collection}")
        except Exception as e:
            logger.error(f"Firestore delete failed: {str(e)}")
