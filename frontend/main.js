const feed = document.getElementById("feed");
const filterBtns = document.querySelectorAll(".filter-btn");
const prevPageBtn = document.getElementById("prevPage");
const nextPageBtn = document.getElementById("nextPage");
const pageInfo = document.getElementById("pageInfo");

let allEvents = [];
let filter = "all";
let page = 1;
const pageSize = 5;

async function fetchEvents() {
  const res = await fetch("/events");
  const data = await res.json();
  allEvents = data;
  renderFeed();
}

function renderFeed() {
  feed.innerHTML = "";

  const filtered = allEvents.filter(e => {
    if (filter === "all") return true;
    return e.action === filter;
  });

  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const visible = filtered.slice(start, end);

  visible.forEach(e => {
    let msg = "";
    const date = new Date(e.timestamp).toLocaleString("en-US", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZoneName: "short",
    });

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

  const totalPages = Math.ceil(filtered.length / pageSize);
  pageInfo.textContent = `Page ${page} of ${totalPages}`;

  prevPageBtn.disabled = page === 1;
  nextPageBtn.disabled = page >= totalPages;
}

filterBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    filterBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    filter = btn.dataset.filter;
    page = 1; // Reset to first page
    renderFeed();
  });
});

prevPageBtn.addEventListener("click", () => {
  if (page > 1) {
    page--;
    renderFeed();
  }
});

nextPageBtn.addEventListener("click", () => {
  page++;
  renderFeed();
});

fetchEvents();
setInterval(fetchEvents, 20000);
