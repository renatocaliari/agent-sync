from agent_sync.validators import validate_repo_name, validate_github_url

def get_github_user():
    return "jules"

name = "my-repo"
print(f"Testing name: {name}")
print(f"validate_repo_name('{name}'): {validate_repo_name(name)}")

repo_name = f"{get_github_user()}/{name}"
repo_url_to_clone = f"https://github.com/{repo_name}.git"
print(f"Constructed URL: {repo_url_to_clone}")
print(f"validate_github_url('{repo_url_to_clone}'): {validate_github_url(repo_url_to_clone)}")

slug = "owner/repo"
print(f"\nTesting slug: {slug}")
print(f"validate_repo_name('{slug}'): {validate_repo_name(slug)}")
