document.addEventListener('DOMContentLoaded', () => {
    // Hamburger menu
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }));

    // API data fetching
    const projectsContainer = document.getElementById('projects-container');
    const apiUrl = 'http://localhost:3000/api/github'; // Replace with your actual API URL

    async function fetchProjects() {
        if (!projectsContainer) return;
        showLoadingIndicator();
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const projects = await response.json();
            renderProjects(projects);

            // After fetching projects, find alexmfv.github.io and render its commits
            const alexmfvRepo = projects.find(repo => repo.name === 'alexmfv.github.io');
            if (alexmfvRepo && alexmfvRepo.commits) {
                renderCommits(alexmfvRepo.commits);
            } else {
                commitsContainer.innerHTML = `<p class="error-message">Commits for alexmfv.github.io not found.</p>`;
            }

        } catch (error) {
            showErrorMessage('Could not fetch projects. Is the API server running?');
            commitsContainer.innerHTML = `<p class="error-message">Could not fetch commits. Is the API server running?</p>`;
            console.error('Error fetching data:', error);
        }
    }

    // This function will now be called from within fetchProjects
    async function fetchCommits() {
        // No longer needed as commits are fetched with projects
    }

    function renderCommits(commits) {
        commitsContainer.innerHTML = '';
        if (!commits || commits.length === 0) {
            commitsContainer.innerHTML = `<p class="error-message">No commits to display.</p>`;
            return;
        }

        commits.slice(0, 5).forEach(commit => {
            const listItem = document.createElement('li');
            listItem.className = 'commit-item';

            const commitDate = new Date(commit.date);
            const dateString = commitDate.toLocaleDateString('en-US', { day: 'numeric', month: 'short' });
            const timeSince = timeAgo(commit.date);
            let badgeText = '';
            if (timeSince.includes('day')) {
                badgeText = 'day';
            } else if (timeSince.includes('week')) {
                badgeText = 'week';
            }

            listItem.innerHTML = `
                <img src="${commit.author.avatar_url}" alt="${commit.author.name}" class="commit-avatar">
                <div class="commit-details">
                    <p class="commit-message">${commit.message}</p>
                    <div class="commit-info">
                        <span class="commit-date">${dateString}</span>
                        ${badgeText ? `<span class="commit-badge">${badgeText}</span>` : ''}
                    </div>
                </div>
            `;
            commitsContainer.appendChild(listItem);
        });
    }

    fetchProjects();
    setInterval(fetchProjects, 5 * 60 * 1000); // Refresh every 5 minutes