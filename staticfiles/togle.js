let toggle = document.querySelector('.toggle');
let navigation = document.querySelector('.navigation');
let main = document.querySelector('.main');
toggle.onclick = function () {

    navigation.classList.toggle('active');
    main.classList.toggle('active');

}
let list = document.querySelectorAll('.navigation li');
function activeLink() {
    list.forEach((item) => item.classList.remove('hovered'));
    this.classList.add('hovered'); // Changed from remove to add
}
list.forEach((item) => item.addEventListener('click', activeLink));