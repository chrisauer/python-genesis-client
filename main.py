from typing import Optional
from models import Student
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re

class AsyncGenesisClient:
    """
    Asynchronous client for interacting with the Genesis student information system.

    This client handles session management and provides methods to fetch student information.

    Attributes:
        base_url (str): The base URL for the Genesis system.
        username (str): Username for authentication.
        password (str): Password for authentication.
        session (aiohttp.ClientSession, optional): The session used for making HTTP requests.

    Methods:
        __aenter__: Initializes the session and authenticates.
        __aexit__: Closes the session upon exit.
        _authenticate: Authenticates the session with provided credentials.
        get_students: Fetches all the students.
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure that the session is created and authenticated"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
            await self._authenticate()

    async def _authenticate(self):
        """Authenticate the session"""
        login_url = f"{self.base_url}/genesis/sis/j_security_check"
        auth_data = {'j_username': self.username, 'j_password': self.password}
        async with self.session.post(login_url, data=auth_data) as response:
            # Check for successful authentication
            if response.status != 200:
                raise Exception("Authentication failed")

    async def close(self):
        if self.session:
            await self.session.close()

    async def get_students(self) -> list[Student]:
        """Get all the students"""
        await self._ensure_session()
        async with self.session.get(f'{self.base_url}/genesis/parents') as response:
            body = await response.text()
            soup = BeautifulSoup(body, 'html.parser')
            students = []
            student_container = soup.select_one("#selectableStudents > div > ul")
            ss = student_container.select('li')
            for s in ss:
                student = Student(
                    genesis_id=re.findall(r"'(.*?)'", s.select_one('a').attrs['onclick'])[0],
                    name=str.splitlines(str.strip(s.select_one('a > div:nth-child(1)').text.replace(u'\xa0', u' ')))[0]
                )
                students.append(student)
            return students


async def main():
    BASE_URL = ""
    USERNAME = ""
    PASSWORD = ""
    async with AsyncGenesisClient(
            base_url=BASE_URL,
            username=USERNAME,
            password=PASSWORD) as client:
        student_info = await client.get_students()
        print(student_info)

if __name__ == '__main__':
    asyncio.run(main())