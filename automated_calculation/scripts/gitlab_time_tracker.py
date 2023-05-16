import requests

# Data to represent team members
team_members = {
    "Andero Raava h": 0,
    "Andero Raava m": 0,
    "Stina Maria Tohver h": 0,
    "Stina Maria Tohver m": 0,
    "Liisi Nõojärv h": 0,
    "Liisi Nõojärv m": 0
}

token_header = {"PRIVATE-TOKEN": "glpat-1yLXqx96-R2BdLzjyumb"}
base_url = "https://gitlab.cs.ttu.ee/api/v4/projects/28408/issues"


def get_issue_idds_from_milestone(sprint_name: str) -> list:
    issues_in_specific_milestone_response = requests.get(f"{base_url}?milestone={sprint_name}&&per_page=100",
                                                         headers=token_header).json()
    issue_iids = [x["iid"] for x in issues_in_specific_milestone_response]
    return issue_iids


def add_time_to_team_members(issue_iids: list):
    for issue_idd in issue_iids:
        comments_in_specific_issue_response = requests.get(f"{base_url}/{issue_idd}/notes", headers=token_header).json()
        for comment in comments_in_specific_issue_response:
            comment_body = comment["body"].split()
            if comment_body[0] == "added":
                for word in comment_body:
                    if word[-1] == "h":
                        team_members[comment["author"]["name"] + " h"] += int(word[:-1])
                    elif word[-1] == "m":
                        team_members[comment["author"]["name"] + " m"] += int(word[:-1])


def convert_excess_m_to_h():
    for member in team_members:
        if member[-1] == "m" and team_members[member] >= 60:
            team_members[member[:-2] + " h"] += team_members[member] // 60
            team_members[member] = team_members[member] % 60

def main():
    # sprint_name = str(input("Sisesta täpselt sprindi/milestonei nimi "))
    all_milestones = [0, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    for i in all_milestones:
        add_time_to_team_members(get_issue_idds_from_milestone(f"Sprint {i}"))
    # print(team_members)
    convert_excess_m_to_h()
    print(team_members)

if __name__ == "__main__":
    main()
