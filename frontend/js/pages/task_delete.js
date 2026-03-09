import { deleteTask, getTask } from "../infra/api.js";

const $task_id = document.getElementById("task_id");
const $check_table = document.getElementById("check_table");
const $task_tbody = document.getElementById("task_tbody");
const $delete_btn = document.getElementById("delete_btn");
const $loading = document.getElementById("loading");
const $registration = document.getElementById("registration");
const $error = document.getElementById("error");


function setBusy (isBusy){
    $delete_btn.disable = isBusy;
    $loading.classList.toggle("is-hidden", !isBusy);
}

function showRegistration(isShow){
    $registration.classList.toggle("is-hidden", !isShow);
}

function showCheckTable(isShow){
    //$task_check.classList.toggle("is-hidden", !isShow);
    $check_table.classList.toggle("is-hidden", !isShow);
}

function showError(e=null, isShow){
    if(e){
        const msg = e?.info?.detail ?? e?.message ?? "Unknown Error";
        $error.textContent = msg;
    }
    
    $error.classList.toggle("is-hidden", !isShow);
}


/**
 * 
 * @param {String|Number|undefined} target  Nullableチェック、変換する文字列
 * @param {StringConstructor|NumberConstructor} type  変換する型コンストラクタ 
 * @returns 
 */
function parseNullable(target, type){
    //console.log(`target : ${target}, typeof : ${typeof target}`)
    if(target === undefined || target ===""){
        return null;
    }

    if(type === Number){
        const n = Number(target);
        return Number.isNaN(n) ? null : n;
    }

    if(type === String){
        return String(target);
    }
}


function getIdFromQuery(){
    const params = new URLSearchParams(window.location.search);
    const idStr = params.get("id");
    const id = Number(idStr);
    if(!idStr || Number.isNaN(id) || id <=0){
        //throw new Error("URLのidが不正です");
        return;
    }
    return id;
}


function renderTable(task){
    const tbody = $task_tbody;
    tbody.innerHTML = "";

    const tr = document.createElement("tr");
    const cells = [
        task.id,
        task.user_id,
        task.title,
        task.description,
        task.status,
        task.priority,
        task.due_date ?? "-"
    ]

    for(const val of cells){
        const td = document.createElement("td");
        td.textContent = val;
        tr.appendChild(td);
    }

    tbody.appendChild(tr);
}


async function getTaskDetail(){
    showCheckTable(false);
    showError(null, false);
    $error.textContent = "";

    let id = parseNullable($task_id.value, Number);
    
    if(id === null){
        return;
    }

    try{
        const task = await getTask(id);
        if(task){
            renderTable(task);
            showCheckTable(true);
        }
 
    } catch(e){
        showError(e, true);
        // showCheckTable(false);
    } 
}


async function deleteTaskID(){
    if(window.confirm("本当に削除しますか？")){
        setBusy(true);
        showRegistration(false);
        showError(null, false);
        $error.textContent = "";

        let result;
        try{
            const task_id = parseNullable($task_id.value, Number);
            result =  await deleteTask(task_id);
            showRegistration(true);
        } catch(e){
            showError(e, true);
        } finally{
            setBusy(false);
        }
    }
}


document.addEventListener("DOMContentLoaded", () => {
    setBusy(false);
    showRegistration(false);
    showError(null, false);
})

$task_id.addEventListener("change", async () => {
    showRegistration(false);
    getTaskDetail();
})

$delete_btn.addEventListener("click", async () => {
    deleteTaskID();
})