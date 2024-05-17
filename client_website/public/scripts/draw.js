const canvas = document.getElementById("paintCanvas")
var canvasRect = canvas.getBoundingClientRect()
canvas.width = canvasRect.width
canvas.height = canvasRect.height

const ctx = canvas.getContext("2d")

ctx.fillStyle = "#E6C25D"
ctx.fillRect(0, 0, canvasRect.width, canvasRect.height)

let prevX = null
let prevY = null

ctx.lineWidth = 8

let draw = false

let clrs = document.querySelectorAll(".clr")
clrs = Array.from(clrs)
clrs.forEach(clr => {
    clr.addEventListener("click", () => {
        ctx.strokeStyle = clr.dataset.clr
    })
})

window.addEventListener("mousedown", (e) => draw = true)
window.addEventListener("mouseup", (e) => draw = false)

window.addEventListener("mousemove", (e) => {
    if(prevX == null || prevY == null || !draw){
        prevX = e.clientX - canvasRect.left
        prevY = e.clientY - canvasRect.top
        return
    }

    let currentX = e.clientX - canvasRect.left
    let currentY = e.clientY - canvasRect.top

    ctx.lineCap = "round"
    ctx.beginPath()
    ctx.moveTo(prevX, prevY)
    ctx.lineTo(currentX, currentY)
    ctx.stroke()

    prevX = currentX
    prevY = currentY
})


let slider = document.getElementById("slider")
slider.addEventListener("click", () => {
    ctx.lineWidth = 2 ** slider.value
});