"""Sample GraphQL documents used by the sample spec."""

GET_USER = """
query GetUser($id: ID!) {
  user(id: $id) {
    id
    username
    email
  }
}
""".strip()

LIST_USERS = """
query ListUsers {
  users {
    id
    username
    email
  }
}
""".strip()
