const feed = document.getElementById("feed");

async function fetchEvents() {
  const res = await fetch("/events");
  const data = await res.json();
  feed.innerHTML = "";

  data.forEach(e => {
    let msg = "";
    const date = new Date(e.timestamp).toUTCString();
    if (e.action === "push") {
      msg = `${e.author} pushed to ${e.to_branch} on ${date}`;
    } else if (e.action === "pull_request") {
      msg = `${e.author} submitted a pull request from ${e.from_branch} to ${e.to_branch} on ${date}`;
    } else if (e.action === "merge") {
      msg = `${e.author} merged branch ${e.from_branch} to ${e.to_branch} on ${date}`;
    }

    const li = document.createElement("li");
    li.textContent = msg;
    feed.appendChild(li);
  });
}

fetchEvents();
setInterval(fetchEvents, 15000);
