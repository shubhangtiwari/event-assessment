/* Dashboard — fetches /admin/api/data, renders stats, groups, and participants. */
(function () {
    'use strict';

    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => Array.from(document.querySelectorAll(sel));

    // -----------------------------------------------------------------
    // Tabs
    // -----------------------------------------------------------------
    $$('.tab').forEach((t) => {
        t.addEventListener('click', () => {
            $$('.tab').forEach((x) => x.classList.remove('active'));
            t.classList.add('active');
            $$('.tab-panel').forEach((p) => p.classList.remove('active'));
            $('#panel-' + t.dataset.tab).classList.add('active');
        });
    });

    // -----------------------------------------------------------------
    // Data fetch + render
    // -----------------------------------------------------------------
    function escapeHtml(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function levelBadge(level) {
        const cls = (level || '').toLowerCase();
        return `<span class="badge ${cls}">${escapeHtml(level)}</span>`;
    }

    function renderStats(data) {
        $('#stat-total').textContent = data.total;
        $('#stat-groups').textContent = data.groups.length;

        if (data.total > 0) {
            const total = data.responses.reduce((s, r) => s + r.score, 0);
            const avg = (total / data.total);
            $('#stat-avg').innerHTML = `${avg.toFixed(1)}<span class="unit">/ 45</span>`;
        } else {
            $('#stat-avg').innerHTML = `—<span class="unit">/ 45</span>`;
        }

        const lc = data.level_counts || {};
        const b = lc['Beginner'] || 0;
        const i = lc['Intermediate'] || 0;
        const a = lc['Advanced'] || 0;
        const T = b + i + a;
        $('#stat-levels').innerHTML = `${b} · ${i} · ${a}`;

        const bar = $('#level-bar');
        if (T > 0) {
            bar.innerHTML =
                `<div class="seg-beginner" style="width:${(b / T * 100).toFixed(1)}%"></div>` +
                `<div class="seg-intermediate" style="width:${(i / T * 100).toFixed(1)}%"></div>` +
                `<div class="seg-advanced" style="width:${(a / T * 100).toFixed(1)}%"></div>`;
        } else {
            bar.innerHTML =
                `<div class="seg-beginner" style="width:33%"></div>` +
                `<div class="seg-intermediate" style="width:33%"></div>` +
                `<div class="seg-advanced" style="width:33%"></div>`;
        }
    }

    function renderGroups(groups) {
        const container = $('#groups-container');
        const empty = $('#groups-empty');
        if (!groups.length) {
            container.innerHTML = '';
            empty.style.display = 'block';
            return;
        }
        empty.style.display = 'none';
        container.innerHTML = groups.map((g) => {
            const mix = g.level_mix || {};
            const meta =
                `${g.size} members · avg ${g.avg_score} · ` +
                `${mix.Beginner || 0}B / ${mix.Intermediate || 0}I / ${mix.Advanced || 0}A`;
            const seats = g.members.map((m, idx) => `
                <li>
                    <span class="seat">${idx + 1}</span>
                    <span class="name" title="${escapeHtml(m.email)}">${escapeHtml(m.name)}</span>
                    ${levelBadge(m.level)}
                    <span class="score">${m.score}</span>
                </li>
            `).join('');
            return `
                <div class="group-card">
                    <h3>Group ${g.number}</h3>
                    <div class="group-meta">${meta}</div>
                    <ol>${seats}</ol>
                </div>
            `;
        }).join('');
    }

    function renderParticipants(responses) {
        const container = $('#participants-container');
        const empty = $('#participants-empty');
        if (!responses.length) {
            container.innerHTML = '';
            empty.style.display = 'block';
            return;
        }
        empty.style.display = 'none';
        const rows = responses.map((r) => `
            <tr>
                <td>${escapeHtml(r.name)}</td>
                <td>${escapeHtml(r.email)}</td>
                <td>${escapeHtml(r.role || '')}</td>
                <td>${escapeHtml(r.years_exp || '')}</td>
                <td><strong>${r.score}</strong></td>
                <td>${levelBadge(r.level)}</td>
                <td style="color: var(--muted); font-size: 12px;">${escapeHtml(r.submitted_at)}</td>
                <td><button class="delete-btn" data-rid="${escapeHtml(r.respondent_id)}" data-name="${escapeHtml(r.name)}">Delete</button></td>
            </tr>
        `).join('');
        container.innerHTML = `
            <table class="data-table">
                <thead><tr>
                    <th>Name</th><th>Email</th><th>Role</th><th>Exp.</th>
                    <th>Score</th><th>Level</th><th>Submitted</th><th></th>
                </tr></thead>
                <tbody>${rows}</tbody>
            </table>
        `;
        container.querySelectorAll('.delete-btn').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const rid = btn.dataset.rid;
                const name = btn.dataset.name;
                if (!confirm(`Delete response from ${name}? This cannot be undone.`)) return;
                btn.disabled = true;
                try {
                    const resp = await fetch('/admin/api/delete/' + encodeURIComponent(rid), {
                        method: 'POST',
                        credentials: 'same-origin',
                    });
                    if (!resp.ok) {
                        alert('Delete failed: ' + resp.status);
                        btn.disabled = false;
                        return;
                    }
                    refresh();
                } catch (err) {
                    alert('Delete failed: ' + err);
                    btn.disabled = false;
                }
            });
        });
    }

    async function refresh() {
        const groupSize = parseInt($('#group-size').value, 10) || 6;
        try {
            const resp = await fetch('/admin/api/data?group_size=' + groupSize, {
                credentials: 'same-origin',
            });
            if (resp.status === 401) {
                window.location.href = '/admin/login';
                return;
            }
            const data = await resp.json();
            renderStats(data);
            renderGroups(data.groups || []);
            renderParticipants(data.responses || []);
        } catch (err) {
            console.error('Failed to load dashboard data', err);
        }
    }

    $('#refresh-btn').addEventListener('click', refresh);
    $('#group-size').addEventListener('change', refresh);

    // -----------------------------------------------------------------
    // Settings
    // -----------------------------------------------------------------
    async function loadSettings() {
        try {
            const resp = await fetch('/admin/api/settings', { credentials: 'same-origin' });
            if (!resp.ok) return;
            const data = await resp.json();
            $('#proxy-url').value = data.proxy_url || '';
        } catch (_) { /* ignore */ }
    }

    $('#settings-form').addEventListener('submit', async function (e) {
        e.preventDefault();
        const status = $('#settings-status');
        status.textContent = 'Saving…';
        try {
            const resp = await fetch('/admin/api/settings', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ proxy_url: $('#proxy-url').value.trim() }),
            });
            if (!resp.ok) {
                status.textContent = 'Save failed (' + resp.status + ')';
                return;
            }
            status.textContent = 'Saved ✓';
            setTimeout(() => { status.textContent = ''; }, 2000);
        } catch (err) {
            status.textContent = 'Save failed: ' + err;
        }
    });

    loadSettings();

    $('#export-btn').addEventListener('click', function (e) {
        e.preventDefault();
        const groupSize = parseInt($('#group-size').value, 10) || 6;
        window.location.href = '/admin/api/export.xlsx?group_size=' + groupSize;
    });

    // Initial load + auto-refresh every 30s so organizers watching the
    // dashboard see new submissions come in live.
    refresh();
    setInterval(refresh, 30000);
})();
