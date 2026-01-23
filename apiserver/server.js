const express = require('express');
const cors = require('cors');
const { Octokit } = require('@octokit/rest');
const fs = require('fs').promises;
const path = require('path');
require('dotenv').config();

const app = express();
app.use(cors());
const port = process.env.PORT || 3000;
const dataFilePath = path.join(__dirname, 'data.json');
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

async function getGitHubData() {
  try {
    const { data: repos } = await octokit.repos.listForAuthenticatedUser({
        visibility: 'all',
        sort: 'pushed',
    });

    const nonForkedRepos = repos.filter(repo => !repo.fork);

    const repoData = await Promise.all(
      nonForkedRepos.map(async (repo) => {
        const { name, description, stargazers_count, html_url, owner } = repo;
        
        let readmeContent = '';
        try {
            const { data: readme } = await octokit.repos.getReadme({
              owner: owner.login,
              repo: name,
            });
            readmeContent = Buffer.from(readme.content, 'base64').toString('utf-8');
        } catch (error) {
            console.error(`Could not fetch README for ${name}:`, error.message);
        }

        let commits = [];
        try {
            const { data: commitData } = await octokit.repos.listCommits({
              owner: owner.login,
              repo: name,
              per_page: 5,
            });
                        commits = commitData.map(commit => ({
                            sha: commit.sha,
                            message: commit.commit.message,
                            date: commit.commit.author.date,
                            author: {
                                name: commit.commit.author.name,
                                avatar_url: commit.author ? commit.author.avatar_url : 'https://via.placeholder.com/30'
                            }
                        }));        } catch (error) {
            console.error(`Could not fetch commits for ${name}:`, error.message);
        }

        return {
          name,
          description,
          stars: stargazers_count,
          url: html_url,
          readme: readmeContent,
          commits,
        };
      })
    );

    return repoData;
  } catch (error) {
    console.error('Error fetching GitHub data:', error);
    throw new Error('Could not fetch data from GitHub');
  }
}

app.get('/api/github', async (req, res) => {
  try {
    let data;
    let lastFetched = 0;

    try {
      const fileContent = await fs.readFile(dataFilePath, 'utf-8');
      const cachedData = JSON.parse(fileContent);
      lastFetched = cachedData.timestamp;
      data = cachedData.data;
    } catch (error) {
      // File does not exist or is invalid, so we fetch new data
    }

    if (Date.now() - lastFetched > CACHE_DURATION) {
      console.log('Cache is stale, fetching new data from GitHub.');
      const newData = await getGitHubData();
      await fs.writeFile(
        dataFilePath,
        JSON.stringify({ timestamp: Date.now(), data: newData }),
        'utf-8'
      );
      data = newData;
    } else {
      console.log('Returning cached data.');
    }

    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
