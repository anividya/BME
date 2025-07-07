function setCurrentDateTime() {
  const currentDateTime = new Date()
  const formattedDateTime = currentDateTime.toISOString().slice(0, 16) // Extracts YYYY-MM-DDTHH:MM
  document.getElementById('workdate').value = formattedDateTime
}

// Call the function to set current date and time on page load
window.onload = setCurrentDateTime
