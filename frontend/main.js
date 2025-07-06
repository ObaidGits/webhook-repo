const feed = document.getElementById("feed");
const filterBtns = document.querySelectorAll(".filter-btn");
const prevPageBtn = document.getElementById("prevPage");
const nextPageBtn = document.getElementById("nextPage");
const pageInfo = document.getElementById("pageInfo");

let allEvents = [];
let filter = "all";
const pageSize = 5;

let latestSeen = null;
let currentPage = 1;
let hasMore = false;

console.log("[INIT] App started.");

async function initialLoad() {
  console.log("[INIT] Initial load...");
  const res = await fetch(`/events?limit=${pageSize}`);
  const data = await res.json();
  console.log("[INIT] Fetched:", data.events.length);
  allEvents = data.events;
  hasMore = data.hasMore;
  if (allEvents.length > 0) {
    latestSeen = allEvents[0].timestamp;
    console.log("[INIT] latestSeen:", latestSeen);
  }
  renderFeed();
}

async function pollNew() {
  if (!latestSeen) return;
  const res = await fetch(`/events?after=${encodeURIComponent(latestSeen)}`);
  const data = await res.json();
  if (data.events.length > 0) {
    allEvents = data.events.concat(allEvents);
    latestSeen = allEvents[0].timestamp;
    renderFeed();
  }
}

async function loadOlder() {
  const filtered = allEvents.filter(e => filter === "all" || e.action === filter);
  const lastVisible = filtered[filtered.length - 1];
  if (!lastVisible) return [];

  const res = await fetch(`/events?before=${encodeURIComponent(lastVisible.timestamp)}&limit=${pageSize}`);
  const data = await res.json();
  if (data.events.length > 0) {
    allEvents = allEvents.concat(data.events);
    hasMore = data.hasMore;
  } else {
    hasMore = false;
  }
  return data.events;
}

function renderFeed() {
  const filtered = allEvents.filter(e => filter === "all" || e.action === filter);
  const end = currentPage * pageSize;
  const visible = filtered.slice(0, end);

  feed.innerHTML = "";
  visible.forEach(e => {
    const date = new Date(e.timestamp).toLocaleString();
    let msg = "";
    if (e.action === "push") {
      msg = `🚀 <strong>${e.author}</strong> pushed to <strong>${e.to_branch}</strong><span>${date}</span>`;
    } else if (e.action === "pull_request") {
      msg = `🔃 <strong>${e.author}</strong> opened a pull request from <strong>${e.from_branch}</strong> to <strong>${e.to_branch}</strong><span>${date}</span>`;
    } else if (e.action === "merge") {
      msg = `✅ <strong>${e.author}</strong> merged branch <strong>${e.from_branch}</strong> into <strong>${e.to_branch}</strong><span>${date}</span>`;
    }
    const li = document.createElement("li");
    li.innerHTML = msg;
    feed.appendChild(li);
  });

  pageInfo.textContent = `Page ${currentPage}`;

  prevPageBtn.style.display = currentPage > 1 ? "inline-block" : "none";
  nextPageBtn.style.display = hasMore || filtered.length > end ? "inline-block" : "none";

  console.log(`[RENDER] allEvents: ${allEvents.length}`);
  console.log(`[RENDER] Filtered: ${filtered.length} Visible: ${visible.length}`);
  console.log(`[RENDER] Current page: ${currentPage}`);
}

filterBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    filterBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    filter = btn.dataset.filter;
    currentPage = 1;
    renderFeed();
  });
});

prevPageBtn.addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage--;
    renderFeed();
  }
});

nextPageBtn.addEventListener("click", async () => {
  const filtered = allEvents.filter(e => filter === "all" || e.action === filter);
  const end = currentPage * pageSize;

  if (filtered.length > end) {
    currentPage++;
    renderFeed();
  } else if (hasMore) {
    const more = await loadOlder();
    if (more.length > 0) {
      currentPage++;
      renderFeed();
    } else {
      hasMore = false;
      renderFeed();
    }
  }
});

initialLoad();
setInterval(pollNew, 15000);
