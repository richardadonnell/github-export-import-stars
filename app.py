import argparse
import logging
import os
import time

from dotenv import load_dotenv
from github import Auth, Github, RateLimitExceededException

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='debug.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Add a stream handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Add debug logging for tokens after logger setup
logger.debug(f"Export token from env: {os.getenv('GITHUB_EXPORT_TOKEN')[:5] if os.getenv('GITHUB_EXPORT_TOKEN') else 'Not set'}...")
logger.debug(f"Import token from env: {os.getenv('GITHUB_IMPORT_TOKEN')[:5] if os.getenv('GITHUB_IMPORT_TOKEN') else 'Not set'}...")

def star_repos(user_export_token, user_import_token, dry_run=True):
    # Create Github instances for both users
    auth1 = Auth.Token(user_export_token)
    auth2 = Auth.Token(user_import_token)
    g1 = Github(auth=auth1, per_page=100)
    g2 = Github(auth=auth2, per_page=100)

    try:
        # Verify authentication for both tokens
        try:
            user1 = g1.get_user()
            user1.login  # This will raise an exception if the token is invalid
            logger.info(f"Successfully authenticated export token for user: {user1.login}")
        except Exception as e:
            logger.error(f"Failed to authenticate export token: {str(e)}")
            return

        try:
            user2 = g2.get_user()
            user2.login  # This will raise an exception if the token is invalid
            logger.info(f"Successfully authenticated import token for user: {user2.login}")
        except Exception as e:
            logger.error(f"Failed to authenticate import token: {str(e)}")
            return

        # Get starred repositories from user1
        starred_repos_user1 = list(user1.get_starred())
        logger.info(f"Found {len(starred_repos_user1)} starred repositories for export user")

        # Get starred repositories from user2
        starred_repos_user2 = list(user2.get_starred())
        logger.info(f"Found {len(starred_repos_user2)} starred repositories for import user")

        # Find repositories that are starred by user1 but not by user2
        repos_to_star = [repo for repo in starred_repos_user1 if repo not in starred_repos_user2]
        logger.info(f"Found {len(repos_to_star)} repositories to star")

        # Always export the list of repos to a text file
        with open('repos_to_star.txt', 'w') as f:
            for repo in repos_to_star:
                f.write(f"{repo.full_name}\n")
        logger.info(f"Exported list of {len(repos_to_star)} repos to star to 'repos_to_star.txt'")

        if not dry_run:
            # Star the repositories for user2 that are not already starred
            for repo in repos_to_star:
                while True:
                    try:
                        user2.add_to_starred(g2.get_repo(repo.full_name))
                        logger.info(f"Starred {repo.full_name}")
                        break
                    except RateLimitExceededException as e:
                        reset_time = e.headers.get('x-ratelimit-reset')
                        retry_after = e.headers.get('retry-after')
                        if retry_after:
                            sleep_time = int(retry_after)
                        elif reset_time:
                            sleep_time = int(reset_time) - int(time.time())
                        else:
                            sleep_time = 60
                        logger.warning(f"Rate limit exceeded. Retrying in {sleep_time} seconds.")
                        time.sleep(sleep_time)
                    except Exception as e:
                        logger.error(f"Failed to star {repo.full_name}: {str(e)}")
                        break
                time.sleep(1)
        else:
            logger.info(f"Dry run completed. {len(repos_to_star)} repositories would be starred.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
    finally:
        g1.close()
        g2.close()
        logger.debug("Closed Github connections")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Star GitHub repositories from one account to another.")
    parser.add_argument("--export-token", help="Access token for the account to export stars from")
    parser.add_argument("--import-token", help="Access token for the account to import stars to")
    parser.add_argument("--run", action="store_true", help="Actually star repositories (default is dry run)")
    args = parser.parse_args()

    logger.debug("Script started with arguments: %s", args)

    export_token = args.export_token or os.getenv('GITHUB_EXPORT_TOKEN')
    import_token = args.import_token or os.getenv('GITHUB_IMPORT_TOKEN')

    logger.debug(f"Export token: {'Set' if export_token else 'Not set'}")
    logger.debug(f"Import token: {'Set' if import_token else 'Not set'}")

    if not export_token or not import_token:
        logger.error("Both export and import tokens are required. Provide them as arguments or in the .env file.")
        exit(1)

    logger.debug(f"Export token starts with: {export_token[:5] if export_token else 'N/A'}...")
    logger.debug(f"Import token starts with: {import_token[:5] if import_token else 'N/A'}...")

    if export_token.startswith('ghp_') and import_token.startswith('ghp_'):
        star_repos(export_token, import_token, not args.run)
    else:
        logger.error(f"Invalid token format. Ensure your tokens start with 'ghp_' and are correctly set in the .env file or provided as arguments.")
        logger.debug(f"Export token prefix: {export_token[:5] if export_token else 'N/A'}")
        logger.debug(f"Import token prefix: {import_token[:5] if import_token else 'N/A'}")
        exit(1)

    logger.debug("Script completed")