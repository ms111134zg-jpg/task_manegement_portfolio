import { getTask, getUser } from "../infra/api.js";

const $task_id = document.getElementById("task_id");
const $task_title = document.getElementById("task_title");
const $task_description = document.getElementById("task_description");
const $task_status = document.getElementById("task_status");
const $task_user = document.getElementById("task_user");
const $task_due = document.getElementById("task_due");
const $task_created = document.getElementById("task_created");
const $task_update = document.getElementById("task_updated");

const $loading = document.getElementById("loading");
const $error = document.getElementById("error");

function setBusy (isBusy){
    $loading.classList.toggle("is-hidden", !isBusy);
}

function showError(e){
    const msg = e?.info?.detail ?? e?.message ?? "Unknown Error";
    $error.textContent = msg;
}

function getIdFromQuery(){
    const params = new URLSearchParams(window.location.search);
    const idStr = params.get("id");
    const id = Number(idStr);
    if(!idStr || Number.isNaN(id) || id <=0){
        throw new Error("URLのidが不正です");
    }
    return id;
}

function convISODateTimeZone(iso){
    const d = new Date(iso);
    const text = d.toLocaleString("ja-JP", {
        timeZone:"Asia/Tokyo",
        year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit", second: "2-digit"
    });
    return text;
}

function renderTask(task, userName){
    $task_id.textContent = task.id;
    $task_title.textContent = task.title;
    $task_description.textContent = task.description;
    $task_status.textContent = task.status;
    $task_user.textContent = userName ?? task.user_id ?? "";
    $task_due.textContent = task.due_date ?? "-";
    $task_created.textContent = convISODateTimeZone(task.created_at);
    $task_update.textContent = convISODateTimeZone(task.updated_at);
}

async function load() {
    setBusy(true);
    $error.textContent = "";

    try{
        const id = getIdFromQuery();
        const task = await getTask(id);

        let userName;
        try{
            if(task.user_id){
                const user = await getUser(task.user_id);
                userName = user.name ?? user.email ?? `user_id:${task.user_id}`; 
            }
        } catch {
        
        }

        renderTask(task,userName);
    } catch(e){
        showError(e);
    } finally{
        setBusy(false);
    }
}

window.addEventListener("DOMContentLoaded", () => {
    load();
})