import { getTask, updateTask, listUsers} from "../infra/api.js"

const $task_id = document.getElementById("task_id");
const $task_check = document.getElementById("task_check");
const $check_table = document.getElementById("check_table");
const $task_tbody = document.getElementById("task_tbody");
const $task_user_id = document.getElementById("task_user_id");
const $task_title = document.getElementById("task_title");
const $task_description = document.getElementById("task_description");
const $task_description_clear = document.getElementById("task_description_clear");
const $task_status = document.getElementById("task_status");
const $task_priority = document.getElementById("task_priority");
const $task_due_date = document.getElementById("task_due_date");
const $task_due_date_clear = document.getElementById("task_due_date_clear");
const $update_btn = document.getElementById("update_btn");
const $loading = document.getElementById("loading");
const $registration = document.getElementById("registration");
const $error = document.getElementById("error");



function setBusy(isBusy){
    $update_btn.disabled = isBusy;
    $loading.classList.toggle("is-hidden", !isBusy);
}

function showRegistration(isShow){
    $registration.classList.toggle("is-hidden", !isShow);
}

function showCheckTable(isShow){
    $task_check.classList.toggle("is-hidden", !isShow);
    $check_table.classList.toggle("is-hidden", !isShow);
}

function showError(e, isShow){
    if(e){
        const msg = e?.info?.detail ?? e?.message ?? "Unknown Error";
        $error.textContent = msg;
    }
    $error.classList.toggle("is-hidden", !isShow);
}





function getIdFromQuery(){
    const params = new URLSearchParams(window.location.search);
    const idStr = params.get("id");
    const id = Number(idStr);
    if(!idStr || Number.isNaN(id) || id <=0){
        return;
    }
    return id;
}


/**
 * 
 * @param {String|Number|undefined} target  Nullableチェック、変換する文字列
 * @param {StringConstructor|NumberConstructor} type  変換する型コンストラクタ 
 * @returns 
 */
function parseNullable(target, type){
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



function readPayloadFromUI(){
    const payload = {};

    let user_id = parseNullable($task_user_id.value, Number);
    let title = parseNullable($task_title.value, String);
    let status = parseNullable($task_status.value, String);
    let priority = parseNullable($task_priority.value, Number);

    let description = parseNullable($task_description.value, String);
    let due_date = parseNullable($task_due_date.value, String);

    const description_check = $task_description_clear;
    const due_date_check = $task_due_date_clear;

    if(user_id)  payload.user_id = user_id;
    if(title) payload.title = title;
    if(status) payload.status = status;
    if(priority) payload.priority = priority;
    if(!description_check.checked){
        if(description) payload.description = description;
    } else{
        payload.description = null;
    }
    if(!due_date_check.checked){
        if(due_date) payload.due_date = due_date;
    } else{
        payload.due_date = null;
    }
    

    return  payload;
        
}


async function getTaskDetail(){
    showCheckTable(false);

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
        showError(e);
    } 
}

async function update(){
    setBusy(true);
    showRegistration(false);
    showError(null, false);
    $error.textContent = "";

    let result;
    try{
        const task_id = parseNullable($task_id.value, Number);
        const payload = readPayloadFromUI();
        result =  await updateTask(task_id, payload);
        showRegistration(true);
    } catch(e){
        showError(e, true);
    } finally{
        setBusy(false);
    }


}


document.addEventListener("DOMContentLoaded", () => {
    setBusy(false);
    showRegistration(false);
    showError(null, false);
   
    const id = getIdFromQuery();
    if(id){
        $task_id.value = Number(id);
        getTaskDetail();
    }

})


$update_btn.addEventListener("click", async () => {
    await update();
    getTaskDetail();
})


$task_id.addEventListener("change", async () => {
    getTaskDetail();
    
})
