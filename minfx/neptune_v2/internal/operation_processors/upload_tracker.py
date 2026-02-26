"""Upload tracker for content-hash based file deduplication.

Tracks uploaded file hashes locally (in-memory per session) to avoid
uploading duplicate files within the same session.

## Design Notes

**Memory usage**: The UploadTracker stores 16-byte hex strings per unique file hash.
Even with 10,000 unique files, this is ~160KB - negligible for any modern system.

**Scope**: Tracking is per-attribute intentionally - the storage layout is
`{experiment_id}/files/{attribute_path}/{hash}.{ext}`, so identical files under
different attributes are stored separately.

**Session scope**: The tracker is intentionally in-memory and session-scoped.
If the process restarts mid-experiment, duplicates may be re-uploaded, but the
backend handles this gracefully by returning existing file (no double-write).
"""

from __future__ import annotations


class UploadTracker:
    """Tracks file hashes that have been uploaded in this session.

    Tracking is per-attribute intentionally: the storage layout is
    `{experiment_id}/files/{attribute_path}/{hash}.{ext}`, so identical
    files under different attributes are stored separately. This simplifies
    the storage model and avoids cross-attribute reference counting.
    """

    def __init__(self) -> None:
        """Initialize the upload tracker with empty hash sets."""
        self._uploaded_hashes: dict[str, set[str]] = {}

    def compute_hash_streaming(self, path: str, chunk_size: int = 8 * 1024 * 1024) -> str:
        """Compute xxHash64 of file content using streaming (memory-efficient).

        Args:
            path: Path to the file to hash.
            chunk_size: Size of chunks to read (default 8MB to match Python client).

        Returns:
            16-character lowercase hex string of the xxHash64 hash.
        """
        import xxhash

        hasher = xxhash.xxh64()
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return format(hasher.intdigest(), "016x")

    def compute_hash(self, data: bytes) -> str:
        """Compute xxHash64 of in-memory bytes.

        Args:
            data: Bytes to hash.

        Returns:
            16-character lowercase hex string of the xxHash64 hash.
        """
        import xxhash

        return format(xxhash.xxh64(data).intdigest(), "016x")

    def is_uploaded(self, attribute: str, content_hash: str) -> bool:
        """Check if this hash was already uploaded for this attribute.

        Args:
            attribute: The attribute path (e.g., "checkpoints/model").
            content_hash: The 16-character hex hash of the content.

        Returns:
            True if this hash was already marked as uploaded for this attribute.
        """
        return content_hash in self._uploaded_hashes.get(attribute, set())

    def mark_uploaded(self, attribute: str, content_hash: str) -> None:
        """Mark hash as uploaded for this attribute.

        Args:
            attribute: The attribute path.
            content_hash: The 16-character hex hash of the content.
        """
        if attribute not in self._uploaded_hashes:
            self._uploaded_hashes[attribute] = set()
        self._uploaded_hashes[attribute].add(content_hash)

    def clear(self) -> None:
        """Clear all tracked hashes (for testing or reset)."""
        self._uploaded_hashes.clear()

    def stats(self) -> dict[str, int]:
        """Get statistics about tracked uploads.

        Returns:
            Dict with attribute -> count of unique hashes.
        """
        return {attr: len(hashes) for attr, hashes in self._uploaded_hashes.items()}
