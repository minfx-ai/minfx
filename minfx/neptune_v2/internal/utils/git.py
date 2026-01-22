#
# Copyright (c) 2022, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import annotations

__all__ = [
    "GitInfo",
    "to_git_info",
    "track_uncommitted_changes",
]

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
)
import warnings

from minfx.neptune_v2.attributes.constants import (
    DIFF_HEAD_INDEX_PATH,
    UPSTREAM_INDEX_DIFF,
)
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.types import File
from minfx.neptune_v2.types.atoms.git_ref import (
    GitRef,
    GitRefDisabled,
)

if TYPE_CHECKING:
    from datetime import datetime

    import git

    from minfx.neptune_v2 import Run

_logger = get_logger()


@dataclass
class GitInfo:
    commit_id: str
    message: str
    author_name: str
    author_email: str
    commit_date: datetime
    dirty: bool
    branch: str | None
    remotes: list[str] | None


def get_git_repo(repo_path: str | None) -> git.Repo | None:
    # WARN: GitPython asserts the existence of `git` executable
    # which consists in failure during the preparation of conda package
    try:
        import git

        return git.Repo(repo_path, search_parent_directories=True)
    except ImportError:
        warnings.warn("GitPython could not be initialized", stacklevel=2)
        return None


def get_repo_from_git_ref(git_ref: GitRef | GitRefDisabled) -> git.Repo | None:
    if git_ref == GitRef.DISABLED:
        return None

    initial_repo_path = git_ref.resolve_path()
    if initial_repo_path is None:
        return None

    try:
        from git.exc import (
            InvalidGitRepositoryError,
            NoSuchPathError,
        )

        try:
            return get_git_repo(repo_path=initial_repo_path)
        except (NoSuchPathError, InvalidGitRepositoryError):
            return None
    except ImportError:
        return None


def to_git_info(git_ref: GitRef | GitRefDisabled) -> GitInfo | None:
    try:
        repo = get_repo_from_git_ref(git_ref)
        commit = repo.head.commit

        active_branch = ""

        try:
            active_branch = repo.active_branch.name
        except TypeError as e:
            if str(e.args[0]).startswith("HEAD is a detached symbolic reference as it points to"):
                active_branch = "Detached HEAD"

        remote_urls = [remote.url for remote in repo.remotes]

        return GitInfo(
            commit_id=commit.hexsha,
            message=commit.message,
            author_name=commit.author.name,
            author_email=commit.author.email,
            commit_date=commit.committed_datetime,
            dirty=repo.is_dirty(index=False, untracked_files=True),
            branch=active_branch,
            remotes=remote_urls,
        )
    except:
        return None


@dataclass
class UncommittedChanges:
    diff_head: str | None
    diff_upstream: str | None
    upstream_sha: str | None


def get_diff(repo: git.Repo, commit_ref: str) -> str | None:
    try:
        from git.exc import GitCommandError

        try:
            diff = repo.git.diff(commit_ref, index=False)

            # add a newline at the end (required to be a valid `patch` file)
            if diff and diff[-1] != "\n":
                diff += "\n"
            return diff
        except GitCommandError:
            return None
    except ImportError:
        return None


def get_relevant_upstream_commit(repo: git.Repo) -> git.Commit | None:
    try:
        tracking_branch = repo.active_branch.tracking_branch()
    except (TypeError, ValueError):
        return None

    if tracking_branch:
        return tracking_branch.commit

    return search_for_most_recent_ancestor(repo)


def search_for_most_recent_ancestor(repo: git.Repo) -> git.Commit | None:
    most_recent_ancestor: git.Commit | None = None

    try:
        from git.exc import GitCommandError

        try:
            for branch in repo.heads:
                tracking_branch = branch.tracking_branch()
                if tracking_branch:
                    for ancestor in repo.merge_base(repo.head, tracking_branch.commit):
                        if not most_recent_ancestor or repo.is_ancestor(most_recent_ancestor, ancestor):
                            most_recent_ancestor = ancestor
        except GitCommandError:
            pass
    except ImportError:
        return None

    return most_recent_ancestor


def get_upstream_index_sha(repo: git.Repo) -> str | None:
    upstream_commit = get_relevant_upstream_commit(repo)

    if upstream_commit and upstream_commit != repo.head.commit:
        return upstream_commit.hexsha
    return None


def get_uncommitted_changes(repo: git.Repo | None) -> UncommittedChanges | None:
    head_index_diff = get_diff(repo, repo.head.name)

    upstream_sha = get_upstream_index_sha(repo)

    upstream_index_diff = get_diff(repo, upstream_sha) if upstream_sha else None
    if head_index_diff or upstream_sha or upstream_index_diff:
        return UncommittedChanges(head_index_diff, upstream_index_diff, upstream_sha)
    return None


def track_uncommitted_changes(git_ref: GitRef | GitRefDisabled, run: Run) -> None:
    repo = get_repo_from_git_ref(git_ref)

    if not repo:
        return

    uncommitted_changes = get_uncommitted_changes(repo)

    if not uncommitted_changes:
        return

    if uncommitted_changes.diff_head:
        run[DIFF_HEAD_INDEX_PATH].upload(File.from_content(uncommitted_changes.diff_head, extension="patch"))

    if uncommitted_changes.diff_upstream:
        run[f"{UPSTREAM_INDEX_DIFF}{uncommitted_changes.upstream_sha}"].upload(
            File.from_content(uncommitted_changes.diff_upstream, extension="patch")
        )
