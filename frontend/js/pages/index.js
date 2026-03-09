import { listTasks } from "../infra/api.js";


//const top_form = document.top_form
const $search_form = document.getElementById("search_form");
const $task_id = document.getElementById("task_id")
const $q_input = document.getElementById("q_input");
const $status_select = document.getElementById("status_select");
const $user_id = document.getElementById("user_id");
const $due_from = document.getElementById("due_from");
const $due_to = document.getElementById("due_to");
const $sort = document.getElementById("sort");
const $order = document.getElementById("order");
const $limit = document.getElementById("limit");
const $page = document.getElementById("page");
const $search_btn = document.getElementById("search_btn");
const $tasks_tbody = document.getElementById("tasks_tbody")
const $loading = document.getElementById("loading");
const $error = document.getElementById("error");



let state = {
    filters : {q : null, status : null, user_id : null, due_from : null, due_to : null},
    pagination : {limit : 50, offset : 0},
    sort : {sort : "id", order : "desc"}
};

let total_tasks = Number(9999);
let isPageChange = false;

//let isBusy = false;
const setBusy = (isBusy) =>{
    $search_btn.disabled = isBusy;
    $loading.classList.toggle("is-hidden", !isBusy);
}

function showError(e=null, isShow){
    if(e){
        const msg = e?.info?.detail ?? e?.message ?? "Unknown Error";
        $error.textContent = msg;
    }
    $error.classList.toggle("is-hidden", !isShow);
}

const readFiltersFromUI = (isPageChange) => {
    let q = $q_input.value;  
    let status = $status_select.value;
    let user_id = $user_id.value;
    let due_from = $due_from.value;
    let due_to = $due_to.value;
    let sort = $sort.value;
    let order = $order.value;
    let limit = $limit.value;
    let page = $page.value;
    let offset = 0;


    if (q === undefined || q ===""){
        q = null;
    }
    if(status === undefined || status === ""){
        status = null;
    }
    if(user_id === undefined || user_id ===""){
        user_id = null;
    } else{
        user_id = Number(user_id);
    }

    if(due_from === undefined || due_from === ""){
        due_from = null;
    }
    if(due_to === undefined || due_to === ""){
        due_to = null;
    }
    if(sort === undefined || sort === ""){
        sort = null;
    }
    if(order === undefined || order === ""){
        order = "desc";
    }
    if(limit === undefined || limit === ""){
        limit = Number(50);
    } else{
        limit = Number(limit);
    }

    if(page === undefined || page === ""){
        page = Number(1);
    } else {
        page = Number(page);
    }

    if(isPageChange){
        offset = (page - 1)*limit;
    } else{
        offset = 0;
        $page.value = 1;
    }

    return [{q: q, status: status, user_id : user_id, due_from : due_from, due_to : due_to}, 
            {limit : limit, offset: offset},
            {sort : sort, order : order}];
}


const applyFilters = (filters) => {
    state.filters = filters[0];
    state.pagination = filters[1];
    state.sort = filters[2];
    //return null;]
}

const buildQueryFromState = () => {
    return {...state.filters,...state.sort,...state.pagination};
}


const renderTable = (rows) => {
    const tbody = $tasks_tbody;
    tbody.innerHTML = ""; 


    for (const row of rows) {
        const tr = document.createElement("tr");

        // 表示したいキー順を決める（列の順番が安定する）
        const cells = [
            row.id,
            row.user_id,
            row.title,
            // row.description,
            row.status,
            row.priority,
            row.due_date ?? "-",  // nullなら "-"
            // row.created_at,
            // row.updated_at
        ];

        for (const val of cells) {
            const td = document.createElement("td");
            td.textContent = String(val);
            tr.appendChild(td);
        }

        // 詳細リンク列
        const DetailLink = document.createElement("td");
        const task_a = document.createElement("a");
        task_a.href = `./task_detail.html?id=${row.id}`;
        task_a.textContent = "詳細";
        DetailLink.appendChild(task_a);
        tr.appendChild(DetailLink);

        // 更新リンク列
        const UpdateLink = document.createElement("td");
        const update_a = document.createElement("a");
        update_a.href = `./task_update.html?id=${row.id}`;
        update_a.textContent = "更新";
        UpdateLink.appendChild(update_a);
        tr.appendChild(UpdateLink);

        tbody.appendChild(tr);
    }
}


const loadTasks = async (isPageChange) => {
    setBusy(true);
    showError( null, false);
    $error.textContent = "";

    let tasks = undefined;

    try{
        applyFilters(readFiltersFromUI(isPageChange));
        const queries = buildQueryFromState();
        tasks = await listTasks(queries);

        total_tasks = tasks.total;

        renderTable(tasks.items);
        setPageMaxNumber();
    } catch (e) {
        showError(e, true);
    } finally{
        setBusy(false);
    }

}


const setPageMaxNumber = () => {
    const limit = Number($limit.value);
    const total = Number(total_tasks);

    const page_max = Math.ceil(total / limit);
    
    $page.setAttribute("max", page_max);
}


window.addEventListener("DOMContentLoaded", async () =>{
    await loadTasks(false);
    setPageMaxNumber();
})




$search_btn.addEventListener("click", (event) =>{
    loadTasks(false);
})


$sort.addEventListener("change", (event) => {
    state.sort.sort = $sort.value;
    loadTasks(false);
})

$order.addEventListener("change", (event) => {
    state.sort.order = $order.value;
    loadTasks(false);
})

$limit.addEventListener("change", (event) => {
    state.pagination.limit = Number($limit.value);
    state.pagination.offset = Number(0);
    $page.value = 1;
    setPageMaxNumber();
    loadTasks(false);
})

$page.addEventListener("change", (event) => {
    const limit = Number($limit.value);
    const page = Number($page.value);
    const offset = Number((page - 1)*limit);
    state.pagination.offset = offset;
    loadTasks(true);
})

