# GitHub Star Transfer

This project allows you to transfer starred repositories from one GitHub account to another. It's a Python script that uses the GitHub API to fetch starred repositories from a source account and star them in a target account.

## Features

- Export starred repositories from one GitHub account
- Import (star) repositories to another GitHub account
- Dry run option to preview actions without making changes
- Detailed logging for debugging and monitoring
- Support for command-line arguments and environment variables

## Prerequisites

- Python 3.6+
- GitHub Personal Access Tokens for both source and target accounts

### Obtaining GitHub Personal Access Tokens

To use this script, you need to create Personal Access Tokens for both the source (export) and target (import) GitHub accounts. Here's how to create them:

1. Log in to your GitHub account.
2. Click on your profile picture in the top-right corner and select "Settings".
3. In the left sidebar, click on "Developer settings".
4. Select "Personal access tokens" and then "Tokens (classic)".
5. Click "Generate new token" and select "Generate new token (classic)".
6. Give your token a descriptive name (e.g., `Star Import/Export`).
7. For the required permissions, select the following scopes:
   - `public_repo`: This allows the script to read public repositories and manage your stars.
   - `read:user`: This allows the script to read user profile data.
8. Click "Generate token" at the bottom of the page.
9. Copy the generated token immediately and store it securely. You won't be able to see it again!

Repeat this process for both the export and import accounts.

**Important:** Keep your tokens secret and secure. Treat them like passwords. Do not share them or expose them in public repositories.

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/github-star-transfer.git
   cd github-star-transfer
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Copy the `.env.example` file to `.env` and fill in your GitHub tokens:

   ```
   cp .env.example .env
   ```

   Edit the `.env` file:

   ```
   GITHUB_EXPORT_TOKEN=your_export_token_here
   GITHUB_IMPORT_TOKEN=your_import_token_here
   ```

   Replace `your_export_token_here` and `your_import_token_here` with the actual tokens you generated.

## Usage

Run the script using the following command:

```
python app.py [--export-token TOKEN] [--import-token TOKEN] [--run]
```

Arguments:

- `--export-token`: Access token for the account to export stars from (optional if set in .env)
- `--import-token`: Access token for the account to import stars to (optional if set in .env)
- `--run`: Actually star repositories (default is dry run)

If tokens are not provided as arguments, the script will use the values from the `.env` file.

### Dry Run (Default)

By default, the script runs in dry run mode. In this mode:

1. It will not actually star any repositories.
2. It will log the repositories it would have starred.
3. It will create a file named `repos_to_star.txt` in the same directory, containing the full names of the repositories that would be starred.

To perform a dry run:

```
python app.py
```

### Actually Starring Repositories

To actually star the repositories, use the `--run` flag:

```
python app.py --run
```

This will perform the actual starring operation.

## Output

The script produces the following outputs:

1. Console output: Displays INFO level messages about the script's progress.
2. `debug.log` file: Contains detailed DEBUG level messages for troubleshooting.
3. `repos_to_star.txt` file: (In dry run mode only) Contains the list of repository full names that would be starred.

## Logging

The script generates two types of logs:

1. Console output: Displays INFO level messages
2. File log: Detailed DEBUG level messages are written to `debug.log`

## Error Handling

The script includes error handling to manage potential issues such as:

- Invalid tokens
- Network errors
- Rate limiting
- Repository access issues

Errors are logged both to the console and the debug log file.

## Security Notes

- Never commit your `.env` file or share your GitHub tokens
- Use tokens with the minimum required permissions (public_repo scope is sufficient)
- Consider using short-lived tokens and rotating them regularly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[GPLv3 License](LICENSE)

## Disclaimer

This tool is not officially associated with GitHub. Use it responsibly and in accordance with GitHub's terms of service.
