import requests

LEETCODE_API = "https://leetcode.com/graphql"

def fetch_leetcode_stats(username):
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """

    variables = {
        "username": username
    }

    response = requests.post(
        LEETCODE_API,
        json={
            "query": query,
            "variables": variables
        }
    )

    data = response.json()

    if not data.get("data") or not data["data"].get("matchedUser"):
        return None

    stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]

    result = {}
    for item in stats:
        result[item["difficulty"]] = item["count"]

    return {
        "total": result.get("All", 0),
        "easy": result.get("Easy", 0),
        "medium": result.get("Medium", 0),
        "hard": result.get("Hard", 0),
    }
