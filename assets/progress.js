"use strict";

const SUBJECTS = ["全部学科","内科学·呼吸","内科学·心血管","内科学·内分泌","外科学","妇产科学","儿科学","传染病学","临床技能","医学心理学","口腔科学","全科医学","眼科学"];
const COHORTS = ["9、11班", "21、22班"];
const $ = (id) => document.getElementById(id);
let storageAvailable = true;
let DATA = [];

function readStored(name, fallback) {
  try { return localStorage.getItem(name) ?? fallback; }
  catch { storageAvailable = false; return fallback; }
}
function readDone() {
  try {
    const saved = JSON.parse(readStored("cheer-share-done", "[]"));
    return new Set(Array.isArray(saved) ? saved.filter((item) => typeof item === "string") : []);
  } catch { return new Set(); }
}
const storedCohort = readStored("cheer-share-cohort", COHORTS[0]);
const state = {
  cohort: COHORTS.includes(storedCohort) ? storedCohort : COHORTS[0],
  scope: "upcoming", subject: "全部学科", type: "全部形式", done: readDone()
};
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const localISO = (d) => [d.getFullYear(), String(d.getMonth()+1).padStart(2,"0"), String(d.getDate()).padStart(2,"0")].join("-");
const today = localISO(new Date());
const future = new Date();
future.setDate(future.getDate() + 21);
const cutoff = localISO(future);
// Keep the original keys so existing browser progress survives the new homepage.
const key = (item) => [item.cohort,item.date || item.dateLabel,item.subject,item.period,item.topic].join("|");
const bounds = (period) => {
  const numbers = (String(period).match(/\d+/g) || []).map(Number);
  return numbers.length ? {start: Math.min(...numbers), end: Math.max(...numbers)} : null;
};

function sessions(items) {
  const result = [];
  for (const item of items) {
    const range = bounds(item.period), previous = result.at(-1), first = previous?.items[0];
    const same = first && first.subject === item.subject && first.type === item.type && first.teacher === item.teacher && first.location === item.location;
    if (previous && range && previous.end !== null && same && range.start === previous.end + 1) {
      previous.items.push(item); previous.end = range.end;
    } else result.push({items:[item],start:range?.start ?? null,end:range?.end ?? null});
  }
  return result;
}
const lessonDone = (session) => session.items.every((item) => state.done.has(key(item)));
function ordered(items) {
  return [...items].sort((a,b) => (a.date || "9999-"+a.week).localeCompare(b.date || "9999-"+b.week, "zh-CN", {numeric:true}) || (bounds(a.period)?.start ?? 99) - (bounds(b.period)?.start ?? 99));
}
function groupDays(items) {
  const groups = new Map();
  ordered(items).forEach((item) => {
    const group = item.date || "第" + item.week + "周 · 集中见习";
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group).push(item);
  });
  return groups;
}
function storageNote() {
  $("storageNote").textContent = storageAvailable
    ? "进度自动保存在当前浏览器，每位访客独立记录。换设备、换浏览器或清除网站数据后不会自动同步。"
    : "当前浏览器无法保存进度，本次勾选仅在当前页面有效。请检查浏览器的网站存储设置。";
}
function writeStored(name, value) {
  try { localStorage.setItem(name, value); storageAvailable = true; }
  catch { storageAvailable = false; }
  storageNote();
}
function save() { writeStored("cheer-share-done", JSON.stringify([...state.done])); }
function announce(message) { $("saveStatus").textContent = storageAvailable ? message : "当前浏览器无法保存，完成记录暂存在本页面。"; }
function selectData() {
  return DATA.filter((item) => item.cohort === state.cohort &&
    (state.subject === "全部学科" || item.subject === state.subject) &&
    (state.type === "全部形式" || item.type === state.type) &&
    (state.scope === "all" || (state.scope === "today" ? item.date === today : item.date && item.date >= today && item.date <= cutoff)));
}
function cohortSessions() {
  return [...groupDays(DATA.filter((item) => item.cohort === state.cohort)).values()].flatMap(sessions);
}
function renderToday() {
  const items = ordered(DATA.filter((item) => item.cohort === state.cohort && item.date === today));
  const groups = sessions(items), completed = groups.filter(lessonDone).length;
  const percent = groups.length ? Math.round(completed/groups.length*100) : 0;
  const semester = cohortSessions();
  $("semesterCount").textContent = "已完成 " + semester.filter(lessonDone).length + " / " + semester.length + " 组课程";
  $("semesterClass").textContent = state.cohort + " · 本学期学习进度";
  $("todayDate").textContent = new Intl.DateTimeFormat("zh-CN", {month:"long",day:"numeric",weekday:"long"}).format(new Date());
  $("todayTitle").textContent = groups.length ? "今天有 " + groups.length + " 组课程" : "今天没有课程安排";
  $("todayText").textContent = groups.length ? [...new Set(items.map((item) => item.subject))].join(" · ") : "留一点时间，复习之前学过的内容，或好好休息。";
  $("todayCount").innerHTML = "<strong>" + completed + "</strong> / " + groups.length + " 组已完成";
  $("todayBar").style.width = percent + "%";
  $("todayTrack").setAttribute("aria-valuenow", String(percent));
  $("finishToday").disabled = !groups.length || completed === groups.length;
  $("finishToday").textContent = groups.length && completed === groups.length ? "今天已全部完成" : "今天全部学完";
}

function render() {
  document.querySelectorAll("#classSwitch button").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.value === state.cohort)));
  document.querySelectorAll("#scopeTabs button").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.value === state.scope)));
  renderToday();
  const items = selectData(), groups = groupDays(items);
  const visible = [...groups.values()].flatMap(sessions), completed = visible.filter(lessonDone).length;
  $("resultTitle").textContent = {today:"今天的课程",upcoming:"接下来要上的课",all:"全部课程安排"}[state.scope];
  $("resultCount").textContent = visible.length + " 组课程 · 已完成 " + completed + " 组";
  if (!items.length) {
    $("timeline").innerHTML = '<div class="progress-empty"><strong>当前筛选下没有课程</strong><p>可以切换时间范围、学科或课程形式。</p></div>';
    return;
  }
  const focused = document.activeElement?.dataset.session;
  let ordinal = 0;
  $("timeline").innerHTML = [...groups].map(([group, rows], groupIndex) => {
    const first = rows[0], daySessions = sessions(rows);
    const date = first.date ? new Intl.DateTimeFormat("zh-CN",{month:"numeric",day:"numeric",weekday:"short"}).format(new Date(first.date+"T12:00:00")) : group;
    return '<section class="progress-day"><div class="progress-date"><strong>'+esc(date)+'</strong><span>'+esc(first.date ? "第 "+first.week+" 周" : first.dateLabel)+'</span><button type="button" data-day="'+groupIndex+'">'+(first.date ? "本日全部完成" : "本组全部完成")+'</button></div><div>'+
      daySessions.map((session) => {
        const item = session.items[0], done = lessonDone(session), index = ordinal++;
        const period = session.start === null ? (item.period || "待定") : session.start === session.end ? String(session.start) : session.start+"—"+session.end;
        const hours = session.items.reduce((sum,row) => sum+(Number(row.hours)||0),0);
        return '<article class="progress-lesson'+(done?' is-complete':'')+'"><div class="progress-period"><strong>'+esc(period)+'</strong><span>节'+(session.items.length>1?' · 连续':'')+'</span></div><div><div class="progress-meta"><span class="progress-kind'+(item.type!=="理论"?' is-practice':'')+'">'+esc(item.type)+'</span><span>'+esc(item.subject)+'</span></div>'+
          session.items.map((row) => '<div class="progress-topic"><h3><small>'+esc(row.period || "待定")+'节</small>'+esc(row.topic)+'</h3></div>').join("")+
          '<p class="progress-details">'+esc([item.teacher,hours?hours+" 学时":"",item.location].filter(Boolean).join(" · "))+'</p></div><button type="button" class="progress-done" data-session="'+index+'" aria-pressed="'+done+'" aria-label="'+esc((done?"取消完成：":"标记完成：")+item.subject+"，"+session.items.map((row)=>row.topic).join("、"))+'"><i class="progress-check" aria-hidden="true"></i>'+(done?"已完成":"标记完成")+'</button></article>';
      }).join("")+'</div></section>';
  }).join("");
  $("timeline").querySelectorAll("[data-session]").forEach((button) => {
    button.onclick = () => {
      const session = visible[Number(button.dataset.session)], done = lessonDone(session);
      session.items.forEach((item) => done ? state.done.delete(key(item)) : state.done.add(key(item)));
      save(); render(); announce(done ? "已取消完成，进度已保存。" : "已完成一组课程，进度已保存。");
    };
  });
  const dayRows = [...groups.values()];
  $("timeline").querySelectorAll("[data-day]").forEach((button) => {
    button.onclick = () => {
      dayRows[Number(button.dataset.day)].forEach((item) => state.done.add(key(item)));
      save(); render(); announce("这一组安排已全部完成，进度已保存。");
    };
  });
  if (focused !== undefined) $("timeline").querySelector('[data-session="'+focused+'"]')?.focus({preventScroll:true});
}

SUBJECTS.forEach((subject) => $("subject").add(new Option(subject, subject)));
$("subject").onchange = (event) => { state.subject=event.target.value; render(); };
$("type").onchange = (event) => { state.type=event.target.value; render(); };
document.querySelectorAll("#classSwitch button").forEach((button) => {
  button.onclick = () => { state.cohort=button.dataset.value; writeStored("cheer-share-cohort",state.cohort); render(); };
});
document.querySelectorAll("#scopeTabs button").forEach((button) => {
  button.onclick = () => { state.scope=button.dataset.value; render(); };
});
$("finishToday").onclick = () => {
  DATA.filter((item) => item.cohort===state.cohort && item.date===today).forEach((item) => state.done.add(key(item)));
  save(); render(); announce("今天的课程已全部完成，进度已保存。");
};
$("reset").onclick = () => {
  if (confirm("确定清除当前浏览器中两个班级的所有完成记录吗？此操作不会影响其他人的进度。")) {
    state.done.clear(); save(); render(); announce("已清除当前浏览器的完成记录。");
  }
};
window.addEventListener("storage", (event) => {
  if (event.key === "cheer-share-done") { state.done=readDone(); if(DATA.length) render(); }
  if (event.key === "cheer-share-cohort" && COHORTS.includes(event.newValue)) {
    state.cohort=event.newValue; if(DATA.length) render();
  }
});

async function initialize() {
  $("status").hidden = false;
  $("status").textContent = "正在加载本学期课程安排。";
  try {
    const response = await fetch("data/schedule.json");
    if (!response.ok) throw new Error("Could not load schedule");
    const data = await response.json();
    if (!Array.isArray(data) || !data.length) throw new Error("Invalid schedule");
    DATA=data; storageNote(); render();
    $("status").hidden=true; $("progressContent").hidden=false;
  } catch {
    $("semesterCount").textContent = "课程安排暂未加载";
    $("status").innerHTML = '课程安排暂时无法加载，请检查网络后重试。 <button class="progress-button" id="retrySchedule" type="button">重新加载</button>';
    $("retrySchedule").onclick=initialize;
  }
}
const ready = initialize();
