function calcAge(b) {
    const d = new Date(b);
    const t = new Date();
    let a = t.getFullYear() - d.getFullYear();
    const m = t.getMonth() - d.getMonth();
    if (m < 0 || (m === 0 && t.getDate() < d.getDate())) {
        a--;
    }
    return a;
}
document.getElementById('age').textContent = calcAge(atob('MjAwMC0xMi0wNA=='));

async function loadProjects() {
    try {
        const response = await fetch('https://api.github.com/users/alexmfv/repos');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const repos = await response.json();
        const projectsContainer = document.getElementById('projects-container');
        repos.forEach(async repo => {
            try {
                const commitsResponse = await fetch(repo.commits_url.replace('{/sha}', ''));
                if (!commitsResponse.ok) {
                    throw new Error('Network response was not ok');
                }
                const commits = await commitsResponse.json();
                const projectItem = document.createElement('div');
                projectItem.className = 'project-item';
                projectItem.innerHTML = `
                    <h4>${repo.name}</h4>
                    <p>${repo.description || 'No description available.'}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <a href="${repo.html_url}" target="_blank">
                            <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" style="width: 20px; height: 20px; margin-right: 10px;">
                        </a>
                        <div style="display: flex; gap: 10px;">
                            <p>⭐ Stars: ${repo.stargazers_count}</p>
                            <p>🍴 Forks: ${repo.forks_count}</p>
                            <p>🔄 Commits: ${commits.length}</p>
                        </div>
                    </div>
                `;
                projectsContainer.appendChild(projectItem);
            } catch (error) {
                console.error('Failed to fetch commits:', error);
            }
        });
    } catch (error) {
        console.error('Failed to fetch repos:', error);
    }
}

loadProjects();