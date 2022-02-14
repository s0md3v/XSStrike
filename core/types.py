
# This file is made to add new types to the project.


# This class is used by requester function in requester.py to return only the html for use of in other functions.
class CustomResponse: 
    def __init__(self, html):
        self.text = html