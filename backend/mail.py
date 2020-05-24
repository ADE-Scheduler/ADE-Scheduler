import smtplib


class Mail:

    def __init__(self, credentials):
        self.credentials = credentials
        self.server = None

    def login(self):
        self.server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        return self.server.login(self.credentials["username"], self.credentials["password"])

    def logout(self):
        return self.server.quit()

    def write_us(self, message):
        self.server.sendmail(
            self.credentials["user"],
            self.credentials["user"],
            message
        )
