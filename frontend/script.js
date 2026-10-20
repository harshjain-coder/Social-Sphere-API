const API_ROOT = ["localhost", "127.0.0.1"].includes(location.hostname)
  ? "http://127.0.0.1:8000/api"
  : "https://social-sphere-api-y2tt.onrender.com/api";

const TALKHUB = `${API_ROOT}/talkhub`;
const API = {
  signup: `${TALKHUB}/SignUp`,
  login: `${API_ROOT}/login/`,
  me: `${API_ROOT}/me/`,
  people: `${TALKHUB}/Person`,
  posts: `${TALKHUB}/Post`,
  comments: `${TALKHUB}/Comment`,
  likes: `${TALKHUB}/Like`,
  saves: `${TALKHUB}/Save`,
  follows: `${TALKHUB}/Follow`,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const state = {
  token: sessionStorage.getItem("ss_access") || "",
  user: null,
  people: [],
  posts: [],
  likes: [],
  comments: [],
  saves: [],
  follows: [],
  sort: "latest",
  search: "",
  authMode: "login",
};

const esc = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const nameOf = (id) => {
  const person = state.people.find((item) => +item.id === +id);
  if (!person) return `Person #${id}`;
  return `${person.first_name || ""} ${person.last_name || ""}`.trim() || person.email || `Person #${id}`;
};

const initials = (name) => name.split(/\s+/).filter(Boolean).slice(0, 2).map((x) => x[0]).join("").toUpperCase() || "S";

const ago = (value) => {
  if (!value) return "Just now";
  const seconds = Math.max(0, (Date.now() - new Date(value)) / 1000);
  if (seconds < 60) return "Just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

function msg(id, text, type = "") {
  const element = $(id);
  if (!element) return;
  element.textContent = text;
  element.className = `inline-message ${type}`;
}

function toast(text) {
  const element = $("#toast");
  if (!element) return;
  element.textContent = text;
  element.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => element.classList.remove("show"), 2600);
}

async function api(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData) && options.body) headers["Content-Type"] = "application/json";
  if (state.token) headers.Authorization = `Bearer ${state.token}`;

  const response = await fetch(url, { ...options, headers });
  const raw = await response.text();
  let data = null;
  try { data = raw ? JSON.parse(raw) : null; } catch { data = raw; }

  if (!response.ok) {
    const detail = data?.detail || data?.message || Object.entries(data || {})
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
      .join(" · ");
    throw Error(detail || `${response.status} ${response.statusText}`);
  }
  return data;
}

function updateUI() {
  const loggedIn = !!state.user;
  $("#loginOpen")?.classList.toggle("hidden", loggedIn);
  $("#signupOpen")?.classList.toggle("hidden", loggedIn);
  $("#logoutButton")?.classList.toggle("hidden", !loggedIn);

  $("#userGreeting").textContent = loggedIn ? `Hi, ${state.user.first_name || state.user.username}` : "";
  $("#profileName").textContent = loggedIn ? `${state.user.first_name} ${state.user.last_name}`.trim() : "Welcome to Social Sphere";
  $("#profileHandle").textContent = loggedIn ? `@${state.user.username}` : "Join the community";
  $("#profileBio").textContent = loggedIn ? (state.user.bio || "Share something with your community.") : "A place for thoughtful conversations and shared moments.";
  $("#profileAvatar").textContent = loggedIn ? initials(`${state.user.first_name} ${state.user.last_name}`) : "S";
  $("#profileAction").textContent = loggedIn ? "Create a post" : "Create your account";

  if (loggedIn) {
    const ownPosts = state.posts.filter((post) => +post.user_id === +state.user.profile_id && !post.is_deleted).length;
    const following = state.follows.filter((follow) => +follow.follower === +state.user.profile_id).length;
    const followers = state.follows.filter((follow) => +follow.following === +state.user.profile_id).length;
    $("#profilePosts").textContent = ownPosts;
    $("#profileFollowing").textContent = following;
    $("#profileFollowers").textContent = followers;
  } else {
    $("#profilePosts").textContent = "—";
    $("#profileFollowing").textContent = "—";
    $("#profileFollowers").textContent = "—";
  }
}

function renderFeed() {
  const host = $("#feedList");
  let posts = state.posts.filter((post) => !post.is_deleted);

  if (state.search) {
    const term = state.search.toLowerCase();
    posts = posts.filter((post) => `${post.content || ""} ${nameOf(post.user_id)}`.toLowerCase().includes(term));
  }

  if (!posts.length) {
    host.innerHTML = `<div class="empty-card"><div class="empty-icon">✦</div><strong>${state.search ? "No matching posts" : "Your sphere is quiet"}</strong><p>${state.search ? "Try another search term." : "Be the first person to share something."}</p></div>`;
    return;
  }

  host.innerHTML = posts.map((post) => {
    const likes = state.likes.filter((item) => +item.post_id === +post.id && !item.deleted_at);
    const comments = state.comments.filter((item) => +item.post_id === +post.id && !item.deleted_at);
    const liked = likes.some((item) => +item.user_id === +(state.user?.profile_id || 0));
    const saved = state.saves.some((item) => +item.post_id === +post.id && !item.deleted_at);
    const author = nameOf(post.user_id);
    const own = state.user && +state.user.profile_id === +post.user_id;

    let media = "";
    if (post.type === "image" && post.image_url) {
      media = `<div class="media-frame"><img class="post-media" src="${esc(post.image_url)}" alt="Shared image" loading="lazy"></div>`;
    }
    if (post.type === "video" && post.video_url) {
      media = `<div class="media-frame"><video class="post-media" src="${esc(post.video_url)}" controls preload="metadata"></video></div>`;
    }

    return `<article class="post-card">
      <div class="post-head">
        <div class="avatar">${esc(initials(author))}</div>
        <div class="post-author"><strong>${esc(author)}</strong><span>${ago(post.created_at)}</span></div>
        <span class="post-kind">${esc(post.type)}</span>
        ${own ? `<button class="icon-button danger" data-delete="${post.id}" title="Delete post">×</button>` : ""}
      </div>
      ${post.content ? `<div class="post-copy">${esc(post.content)}</div>` : ""}
      ${media}
      <div class="post-stats"><span>${likes.length} likes</span><span>${comments.length} comments</span></div>
      <div class="post-actions">
        <button class="post-action ${liked ? "liked" : ""}" data-like="${post.id}">${liked ? "♥ Liked" : "♡ Like"}</button>
        <button class="post-action" data-comment="${post.id}">▢ Comment</button>
        <button class="post-action ${saved ? "saved" : ""}" data-save="${post.id}">${saved ? "▣ Saved" : "▱ Save"}</button>
      </div>
    </article>`;
  }).join("");
}

function renderPeople() {
  const host = $("#peopleList");
  if (!state.people.length) {
    host.innerHTML = `<div class="empty-card">No people found yet.</div>`;
    return;
  }
  host.innerHTML = state.people.map((person) => {
    const personName = `${person.first_name || ""} ${person.last_name || ""}`.trim() || "Social Sphere member";
    const following = state.user && state.follows.some((item) => +item.follower === +state.user.profile_id && +item.following === +person.id);
    return `<article class="person-card">
      <div class="avatar large">${esc(initials(personName))}</div>
      <div class="person-copy"><strong>${esc(personName)}</strong><span>@${esc(person.username || "member")}</span><p>${esc(person.bio || "Sharing moments on Social Sphere.")}</p></div>
      ${state.user && +state.user.profile_id !== +person.id ? `<button class="button ${following ? "button-outline" : "button-primary"}" data-follow="${person.id}">${following ? "Following" : "Follow"}</button>` : ""}
    </article>`;
  }).join("");
}

function renderSaved() {
  const host = $("#savedList");
  const savedIds = new Set(state.saves.filter((item) => !item.deleted_at).map((item) => +item.post_id));
  const posts = state.posts.filter((post) => savedIds.has(+post.id) && !post.is_deleted);
  if (!state.user) {
    host.innerHTML = `<div class="empty-card"><div class="empty-icon">▱</div><strong>Log in to see saved posts</strong><p>Your saved posts will appear here.</p></div>`;
    return;
  }
  if (!posts.length) {
    host.innerHTML = `<div class="empty-card"><div class="empty-icon">▱</div><strong>No saved posts yet</strong><p>Tap Save on a post to keep it here.</p></div>`;
    return;
  }
  const original = $("#feedList").innerHTML;
  $("#feedList").innerHTML = "";
  host.innerHTML = posts.map((post) => `<div class="saved-mini"><div><strong>${esc(nameOf(post.user_id))}</strong><span>${esc(post.content || `${post.type} post`)}</span></div><button class="post-action saved" data-save="${post.id}">▣ Saved</button></div>`).join("");
  void original;
}

async function load() {
  try {
    const query = state.sort === "trending" ? "?sort=trending" : "";
    const [posts, people, likes, comments, follows] = await Promise.all([
      api(`${API.posts}${query}`), api(API.people), api(API.likes), api(API.comments), api(API.follows),
    ]);
    state.posts = posts;
    state.people = people;
    state.likes = likes;
    state.comments = comments;
    state.follows = follows;
    state.saves = state.user ? await api(API.saves) : [];
    renderFeed();
    renderPeople();
    renderSaved();
    updateUI();
    $("#apiStatus").textContent = "API connected";
    $("#apiDot").className = "status-dot connected";
  } catch (error) {
    $("#apiStatus").textContent = "API unavailable";
    $("#apiDot").className = "status-dot error";
    $("#feedList").innerHTML = `<div class="empty-card"><div class="empty-icon">!</div><strong>Could not load the feed</strong><p>${esc(error.message)}</p></div>`;
  }
}

function setAuthMode(mode) {
  state.authMode = mode;
  const signup = mode === "signup";
  $("#nameFields").classList.toggle("hidden", !signup);
  $("#emailField").classList.toggle("hidden", !signup);
  $("#email").required = signup;
  $$(".auth-tab").forEach((button) => button.classList.toggle("active", button.dataset.authMode === mode));
  $("#authTitle").textContent = signup ? "Create your sphere." : "Good to have you here.";
  $("#authDescription").textContent = signup ? "Set up your account in a few seconds." : "Log in to join the conversation.";
  $("#authSubmit").innerHTML = signup ? "Create account <span>↗</span>" : "Log in <span>↗</span>";
  msg("#authMessage", "");
}

async function authSubmit(event) {
  event.preventDefault();
  const signup = state.authMode === "signup";
  const username = $("#username").value.trim();
  const password = $("#password").value;
  msg("#authMessage", signup ? "Creating your account…" : "Signing you in…");

  try {
    if (signup) {
      await api(API.signup, {
        method: "POST",
        body: JSON.stringify({
          username,
          email: $("#email").value.trim(),
          first_name: $("#firstName").value.trim(),
          last_name: $("#lastName").value.trim(),
          password,
        }),
      });
    }

    const token = await api(API.login, { method: "POST", body: JSON.stringify({ username, password }) });
    state.token = token.access;
    sessionStorage.setItem("ss_access", token.access);
    state.user = await api(API.me);
    $("#authModal").classList.add("hidden");
    $("#authForm").reset();
    setAuthMode("login");
    updateUI();
    await load();
    toast(signup ? "Welcome to Social Sphere!" : "Welcome back!");
  } catch (error) {
    msg("#authMessage", error.message, "error");
  }
}

async function createPost(event) {
  event.preventDefault();
  if (!state.user) return openAuth("login");

  const type = $("#postType").value;
  const content = $("#postContent").value.trim();
  const file = $("#mediaFile").files[0];

  if (type === "text" && !content) return msg("#createMessage", "Write something first.", "error");
  if (type !== "text" && !file) return msg("#createMessage", `Choose a ${type} file before publishing.`, "error");

  const max = type === "image" ? 10 * 1024 * 1024 : 100 * 1024 * 1024;
  if (file && file.size > max) return msg("#createMessage", `File is too large. Maximum ${type === "image" ? "10 MB" : "100 MB"}.`, "error");

  const body = type === "text" ? JSON.stringify({ type, content }) : new FormData();
  if (body instanceof FormData) {
    body.append("type", type);
    body.append("content", content);
    body.append("media_file", file);
  }

  msg("#createMessage", "Publishing…");
  try {
    await api(API.posts, { method: "POST", body });
    $("#createPostForm").reset();
    updateMediaField();
    await load();
    showView("home");
    toast("Post published successfully");
  } catch (error) {
    msg("#createMessage", error.message, "error");
  }
}

function updateMediaField() {
  const type = $("#postType").value;
  const enabled = type !== "text";
  $("#mediaField").classList.toggle("hidden", !enabled);
  $("#mediaFile").required = enabled;
  $("#mediaFile").accept = type === "image" ? "image/jpeg,image/png,image/gif,image/webp" : "video/mp4,video/webm,video/quicktime,.m4v,.ogv";
  $("#contentLabel").textContent = type === "text" ? "What's on your mind?" : "Description / caption (optional)";
  $("#postContent").required = type === "text";
  $("#mediaUploadLabel").textContent = type === "image" ? "Choose an image" : "Choose a video";
  $("#mediaUploadHint").textContent = type === "image" ? "JPG, PNG, GIF or WEBP · maximum 10 MB" : "MP4, WEBM, MOV, M4V or OGV · maximum 100 MB";
  $("#mediaPreview").classList.add("hidden");
  $("#mediaPreview").innerHTML = "";
}

function previewMedia() {
  const file = $("#mediaFile").files[0];
  const type = $("#postType").value;
  const preview = $("#mediaPreview");
  if (!file || type === "text") return;
  const url = URL.createObjectURL(file);
  preview.classList.remove("hidden");
  preview.innerHTML = type === "image"
    ? `<img class="preview-media" src="${url}" alt="Preview">`
    : `<video class="preview-media" src="${url}" controls></video>`;
}

function showView(view) {
  $$(".view").forEach((element) => element.classList.toggle("active", element.id === `view-${view}`));
  $$(".side-link").forEach((element) => element.classList.toggle("active", element.dataset.view === view));
  if (view === "create" && !state.user) return openAuth("login");
  if (view === "saved" && !state.user) return openAuth("login");
}

function openAuth(mode = "login") {
  setAuthMode(mode);
  $("#authModal").classList.remove("hidden");
  setTimeout(() => $("#username")?.focus(), 50);
}

function closeAuth() {
  $("#authModal").classList.add("hidden");
  msg("#authMessage", "");
}

async function like(id) {
  if (!state.user) return openAuth("login");
  try {
    const existing = state.likes.find((item) => +item.post_id === +id && +item.user_id === +state.user.profile_id && !item.deleted_at);
    if (existing) await api(`${API.likes}/${existing.id}`, { method: "DELETE" });
    else await api(API.likes, { method: "POST", body: JSON.stringify({ post_id: id }) });
    await load();
  } catch (error) { toast(error.message); }
}

async function save(id) {
  if (!state.user) return openAuth("login");
  try {
    const existing = state.saves.find((item) => +item.post_id === +id && !item.deleted_at);
    if (existing) await api(`${API.saves}/${existing.id}`, { method: "DELETE" });
    else await api(API.saves, { method: "POST", body: JSON.stringify({ post_id: id }) });
    await load();
  } catch (error) { toast(error.message); }
}

async function follow(id) {
  if (!state.user) return openAuth("login");
  const existing = state.follows.find((item) => +item.follower === +state.user.profile_id && +item.following === +id);
  try {
    if (existing) await api(`${API.follows}/${existing.id}`, { method: "DELETE" });
    else await api(API.follows, { method: "POST", body: JSON.stringify({ following_id: id }) });
    await load();
  } catch (error) { toast(error.message); }
}

async function deletePost(id) {
  if (!confirm("Delete this post?")) return;
  try {
    await api(`${API.posts}/${id}`, { method: "DELETE" });
    await load();
    toast("Post deleted");
  } catch (error) { toast(error.message); }
}

$("#authForm").addEventListener("submit", authSubmit);
$("#createPostForm").addEventListener("submit", createPost);
$("#postType").addEventListener("change", updateMediaField);
$("#mediaFile").addEventListener("change", previewMedia);
$("#loginOpen").addEventListener("click", () => openAuth("login"));
$("#signupOpen").addEventListener("click", () => openAuth("signup"));
$("#logoutButton").addEventListener("click", () => {
  state.user = null;
  state.token = "";
  sessionStorage.removeItem("ss_access");
  updateUI();
  load();
  toast("You have been logged out");
});

$$("[data-view]").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
$$("[data-auth-mode]").forEach((button) => button.addEventListener("click", () => setAuthMode(button.dataset.authMode)));
$$('[data-close-modal]').forEach((element) => element.addEventListener("click", closeAuth));

$("#profileAction").addEventListener("click", () => state.user ? showView("create") : openAuth("signup"));
$("#refreshFeed").addEventListener("click", load);
$("#openTrending").addEventListener("click", () => {
  state.sort = "trending";
  $$(".feed-tab").forEach((button) => button.classList.toggle("active", button.dataset.sort === "trending"));
  showView("home");
  load();
});

$$('.feed-tab').forEach((button) => button.addEventListener("click", () => {
  state.sort = button.dataset.sort;
  $$(".feed-tab").forEach((item) => item.classList.toggle("active", item === button));
  load();
}));

$("#searchInput").addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  state.search = event.currentTarget.value.trim();
  state.sort = "latest";
  showView("home");
  renderFeed();
});

document.addEventListener("click", (event) => {
  const likeButton = event.target.closest("[data-like]");
  if (likeButton) return like(+likeButton.dataset.like);
  const saveButton = event.target.closest("[data-save]");
  if (saveButton) return save(+saveButton.dataset.save);
  const deleteButton = event.target.closest("[data-delete]");
  if (deleteButton) return deletePost(+deleteButton.dataset.delete);
  const followButton = event.target.closest("[data-follow]");
  if (followButton) return follow(+followButton.dataset.follow);
  const commentButton = event.target.closest("[data-comment]");
  if (commentButton) {
    showView("home");
    toast("Comment API is ready — comment UI can be added next.");
  }
});

async function init() {
  updateMediaField();
  if (state.token) {
    try { state.user = await api(API.me); }
    catch { state.user = null; state.token = ""; sessionStorage.removeItem("ss_access"); }
  }
  updateUI();
  await load();
}

init();