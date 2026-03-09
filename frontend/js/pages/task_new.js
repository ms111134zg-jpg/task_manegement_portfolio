import { listUsers, createTask } from "../infra/api.js";

const $user_id = document.getElementById("user_id");
const $title = document.getElementById("title");
const $description = document.getElementById("description");
const $status = document.getElementById("status");
const $priority = document.getElementById("priority");
const $due_date = document.getElementById("due_date");
const $create_btn = document.getElementById("create_btn");

const $loading = document.getElementById("loading");
const $error = document.getElementById("error");
const $registration = document.getElementById("registration");

function setBusy (isBusy){
    $create_btn.disabled = isBusy;
    $loading.classList.toggle("is-hidden", !isBusy);
}

function showError(e=null, isShow){
    if(e){
        const msg = e?.info?.detail ?? e?.message ?? "Unknown Error";
        $error.textContent = msg;
    }
    $error.classList.toggle("is-hidden", !isShow);
}

function showRegistration(isReg){
    $registration.classList.toggle("is-hidden", !isReg);
}


async function createUserOption(){
    let select = $user_id;

    try{
        const users = await listUsers({limit: 200, offset: 0});

        // for(let num in users){
        //     let user_id = Number(users[num].id);
        //     let name = users[num].name;

        //     let op = document.createElement("option");
        //     op.setAttribute("value", user_id);
        //     op.textContent= name;
        //     select.appendChild(op);
        // }
        for(let user of users){

            let user_id = Number(user.id);
            let name = user.name;

            let op = document.createElement("option");
            op.setAttribute("value", user_id);
            op.textContent= name;
            select.appendChild(op);
        
        }
    } catch(e) {
        showError(e, true);
    }
}


function readPayloadFromUI(){
    let user_id = $user_id.value;
    let title = $title.value;
    let description = $description.value;
    let status = $status.value;
    let priority = $priority.value;
    let due_date = $due_date.value;

    if( user_id === undefined || user_id === ""){
        user_id = null;
    } else{
        user_id = Number(user_id);
    }

    if( title === undefined || title === ""){
       title = null; 
    }
    if( description === undefined || description === ""){
        description = null;
    }
    if( status === undefined || status === ""){
        status = null;
    }
    if( priority === undefined || priority === ""){
        priority = null;
    } else{
        priority = Number(priority);
    }

    if( due_date === undefined || due_date === ""){
        due_date = null;
    }
    
    const payload = {
        user_id : Number(user_id),
        title : title,
        description : description,
        status : status,
        priority : priority,
        due_date : due_date
    }

    return payload;
}


async function create(){
    setBusy(true);
    showRegistration(false);
    showError(null, false);
    $error.textContent = "";

    let result;

    try{
        const payload = readPayloadFromUI();
        result = await createTask(payload);
        showRegistration(true);
    } catch(e){
        showError(e, true);
    } finally{
        setBusy(false);
    }

    //return result;

}


document.addEventListener("DOMContentLoaded", () => {
    setBusy(false);
    showRegistration(false);
    showError(null, false);
    createUserOption();
})


$create_btn.addEventListener("click", (event) => {
    create();
})

