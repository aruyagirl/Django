const usernameField=document.querySelector('#usernameField');
const emailField=document.querySelector('#emailField');
const usernamefeedBackArea=document.querySelector('.invalid-username');
const emailfeedBackArea = document.querySelector('.invalid-email');
const passwordField = document.querySelector('#passwordField')
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const emailSuccessOutput = document.querySelector('.emailSuccessOutput');
const showPasswordToggle=document.querySelector('.showPasswordToggle');


usernameField.addEventListener('keyup', (e) => {
    const usernameVal = e.target.value;

    usernameSuccessOutput.style.display = "block";
    
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`;

    usernameField.classList.remove('is-invalid');
    usernamefeedBackArea.style.display='none';

    if(usernameVal.length > 0) {
        fetch("/authentication/validate-username", {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) =>{
                console.log("data", data);
                usernameSuccessOutput.style.display="none"
            if (data.username_error){
                usernameField.classList.add('is-invalid');
                usernamefeedBackArea.style.display='block';
                usernamefeedBackArea.innerHTML=`<p>${data.username_error}</p>`;
            } else {
                // Remove error state without showing success message
                usernameField.classList.remove('is-invalid');
                usernamefeedBackArea.style.display = 'none';
            }
        });
    }
});

emailField.addEventListener('keyup', (e) => {
    const emailVal = e.target.value;

    emailSuccessOutput.style.display = "block";
    
    emailSuccessOutput.textContent = `Checking ${emailVal}`;

    emailField.classList.remove("is-invalid");
    emailfeedBackArea.style.display = "none";

    if (emailVal.length > 0) {
        fetch("/authentication/validate-email", {
            body: JSON.stringify({ email: emailVal }),
            method:"POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data);
                emailSuccessOutput.style.display="none"
            if (data.email_error) {
                emailField.classList.add('is-invalid');
                emailfeedBackArea.style.display = 'block';
                emailfeedBackArea.innerHTML=`<p>${data.email_error}</p>`;
            } else {
                // Remove error state without showing success message
                emailField.classList.remove('is-invalid');
                emailfeedBackArea.style.display = 'none';
            }
        });
    }
});

const handleToggleInput=(e)=>{
    if (showPasswordToggle.textContent==='SHOW'){
        showPasswordToggle.textContent='HIDE';
        passwordField.setAttribute("type","text");
    } else {
        showPasswordToggle.textContent="SHOW";
        passwordField.setAttribute("type","password");
    }
};

showPasswordToggle.addEventListener('click', handleToggleInput);