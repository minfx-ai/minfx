#
# Copyright (c) 2019, Neptune Labs Sp. z o.o.
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


class GitInfo:
    """Class that keeps information about a git repository in experiment.

    When :meth:`~neptune.projects.Project.create_experiment` is invoked, instance of this class is created to
    store information about git repository.
    This information is later presented in the experiment details tab in the Neptune web application.

    Args:
        commit_id (:obj:`str`): commit id sha.
        message (:obj:`str`, optional, default is ``""``): commit message.
        author_name (:obj:`str`, optional, default is ``""``): commit author username.
        author_email (:obj:`str`, optional, default is ``""``): commit author email.
        commit_date (:obj:`datetime.datetime`, optional, default is ``""``): commit datetime.
        repository_dirty (:obj:`bool`, optional, default is ``True``):
            ``True``, if the repository has uncommitted changes, ``False`` otherwise.
    """

    def __init__(
        self,
        commit_id: str,
        message: str = "",
        author_name: str = "",
        author_email: str = "",
        commit_date: str = "",
        repository_dirty: bool = True,
        active_branch: str = "",
        remote_urls: list[str] | None = None,
    ) -> None:
        if remote_urls is None:
            remote_urls = []
        if commit_id is None:
            raise TypeError("commit_id must not be None")

        self.commit_id = commit_id
        self.message = message
        self.author_name = author_name
        self.author_email = author_email
        self.commit_date = commit_date
        self.repository_dirty = repository_dirty
        self.active_branch = active_branch
        self.remote_urls = remote_urls

    def __eq__(self, o: object) -> bool:
        return o is not None and self.__dict__ == o.__dict__

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(
            (
                self.commit_id,
                self.message,
                self.author_name,
                self.author_email,
                self.commit_date,
                self.repository_dirty,
                self.active_branch,
                tuple(self.remote_urls) if self.remote_urls else None,
            )
        )

    def __str__(self) -> str:
        return f"GitInfo({self.commit_id})"

    def __repr__(self) -> str:
        return str(self)
