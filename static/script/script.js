function triggerButtonClick(id) // имитирует клик на id
{
    document.getElementById(id).click();
}

function changeColorInfo(id)  // если регистрация прошла успешно красит надпись в зеленый
{
    info = document.getElementById(id)

    if(info.innerHTML == 'You have successfully registered' || info.innerHTML == 'Password changed successfully' || info.innerHTML == 'You have successfully changed your mail' || info.innerHTML == 'Login changed successfully'){
        info.style.color = 'green'
    }else{
        info.style.color = 'red'
    }
}

function send_mail(endpoint, whichmail, subject) // отправляет письмо с кодом подтверждения
{
    const error = document.getElementById('error')
    if(!error.innerHTML){
        const code = document.cookie.match(/rand=([0-9]+)/)[1]
        const re = `${whichmail}=(.*?)[;$]`
        const pattern = new RegExp(re)
        console.log(document.cookie)
        const mail = document.cookie.match(pattern)[1]
        console.log(mail)
        window.location.replace(`https://my-smtp.000webhostapp.com?to=${mail}&from=noreply@company.com&subject=${subject}&message=Code: ${code}&endpoint=${endpoint}`)
    }
}