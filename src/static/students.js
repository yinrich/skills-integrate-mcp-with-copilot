document.addEventListener("DOMContentLoaded", () => {
  const studentsList = document.getElementById("students-list");
  const studentForm = document.getElementById("student-form");
  const formTitle = document.getElementById("form-title");
  const submitBtn = document.getElementById("submit-btn");
  const cancelBtn = document.getElementById("cancel-btn");
  const formMessage = document.getElementById("form-message");
  const searchInput = document.getElementById("search");
  const gradeFilter = document.getElementById("grade-filter");
  const exportBtn = document.getElementById("export-btn");
  const modal = document.getElementById("student-modal");
  const modalClose = document.querySelector(".close");

  let isEditMode = false;

  // Fetch and display students
  async function fetchStudents() {
    try {
      const searchQuery = searchInput.value.trim();
      const gradeValue = gradeFilter.value;
      
      let url = "/students";
      const params = new URLSearchParams();
      if (searchQuery) params.append("search", searchQuery);
      if (gradeValue) params.append("grade", gradeValue);
      if (params.toString()) url += `?${params.toString()}`;

      const response = await fetch(url);
      const students = await response.json();

      // Clear loading message
      studentsList.innerHTML = "";

      if (Object.keys(students).length === 0) {
        studentsList.innerHTML = "<p>No students found.</p>";
        return;
      }

      // Create student cards
      Object.entries(students).forEach(([email, student]) => {
        const studentCard = document.createElement("div");
        studentCard.className = "student-card";

        studentCard.innerHTML = `
          <div class="student-info">
            <h4>${student.name}</h4>
            <p><strong>Email:</strong> ${student.email}</p>
            <p><strong>Grade:</strong> ${student.grade}</p>
          </div>
          <div class="student-actions">
            <button class="view-btn" data-email="${email}">View</button>
            <button class="edit-btn" data-email="${email}">Edit</button>
            <button class="delete-btn" data-email="${email}">Delete</button>
          </div>
        `;

        studentsList.appendChild(studentCard);
      });

      // Add event listeners
      document.querySelectorAll(".view-btn").forEach((btn) => {
        btn.addEventListener("click", handleViewStudent);
      });
      document.querySelectorAll(".edit-btn").forEach((btn) => {
        btn.addEventListener("click", handleEditStudent);
      });
      document.querySelectorAll(".delete-btn").forEach((btn) => {
        btn.addEventListener("click", handleDeleteStudent);
      });
    } catch (error) {
      studentsList.innerHTML = "<p>Failed to load students. Please try again later.</p>";
      console.error("Error fetching students:", error);
    }
  }

  // Handle view student
  async function handleViewStudent(event) {
    const email = event.target.getAttribute("data-email");

    try {
      // Fetch student details
      const studentResponse = await fetch(`/students/${encodeURIComponent(email)}`);
      const student = await studentResponse.json();

      // Fetch student activities
      const activitiesResponse = await fetch(`/students/${encodeURIComponent(email)}/activities`);
      const activities = await activitiesResponse.json();

      // Populate modal
      document.getElementById("modal-student-name").textContent = student.name;
      document.getElementById("modal-student-info").innerHTML = `
        <p><strong>Email:</strong> ${student.email}</p>
        <p><strong>Grade:</strong> ${student.grade}</p>
      `;

      const activitiesDiv = document.getElementById("modal-student-activities");
      if (activities.length === 0) {
        activitiesDiv.innerHTML = "<p><em>Not enrolled in any activities</em></p>";
      } else {
        activitiesDiv.innerHTML = `
          <ul>
            ${activities.map(activity => `
              <li>
                <strong>${activity.name}</strong><br>
                ${activity.description}<br>
                <em>${activity.schedule}</em>
              </li>
            `).join("")}
          </ul>
        `;
      }

      // Show modal
      modal.classList.remove("hidden");
    } catch (error) {
      showMessage("Failed to load student details.", "error");
      console.error("Error viewing student:", error);
    }
  }

  // Handle edit student
  async function handleEditStudent(event) {
    const email = event.target.getAttribute("data-email");

    try {
      const response = await fetch(`/students/${encodeURIComponent(email)}`);
      const student = await response.json();

      // Fill form with student data
      document.getElementById("student-name").value = student.name;
      document.getElementById("student-email").value = student.email;
      document.getElementById("student-grade").value = student.grade;
      document.getElementById("original-email").value = email;

      // Switch to edit mode
      isEditMode = true;
      formTitle.textContent = "Edit Student";
      submitBtn.textContent = "Update Student";
      cancelBtn.style.display = "inline-block";

      // Scroll to form
      document.getElementById("student-form-section").scrollIntoView({ behavior: "smooth" });
    } catch (error) {
      showMessage("Failed to load student for editing.", "error");
      console.error("Error loading student:", error);
    }
  }

  // Handle delete student
  async function handleDeleteStudent(event) {
    const email = event.target.getAttribute("data-email");

    if (!confirm(`Are you sure you want to delete this student?`)) {
      return;
    }

    try {
      const response = await fetch(`/students/${encodeURIComponent(email)}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchStudents();
      } else {
        showMessage(result.detail || "Failed to delete student", "error");
      }
    } catch (error) {
      showMessage("Failed to delete student. Please try again.", "error");
      console.error("Error deleting student:", error);
    }
  }

  // Handle form submission
  studentForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("student-name").value;
    const email = document.getElementById("student-email").value;
    const grade = document.getElementById("student-grade").value;
    const originalEmail = document.getElementById("original-email").value;

    const studentData = { name, email, grade };

    try {
      let response;

      if (isEditMode) {
        // Update student
        response = await fetch(`/students/${encodeURIComponent(originalEmail)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(studentData),
        });
      } else {
        // Create student
        response = await fetch("/students", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(studentData),
        });
      }

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        resetForm();
        fetchStudents();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to save student. Please try again.", "error");
      console.error("Error saving student:", error);
    }
  });

  // Cancel edit
  cancelBtn.addEventListener("click", resetForm);

  // Reset form
  function resetForm() {
    studentForm.reset();
    document.getElementById("original-email").value = "";
    isEditMode = false;
    formTitle.textContent = "Add New Student";
    submitBtn.textContent = "Add Student";
    cancelBtn.style.display = "none";
    formMessage.classList.add("hidden");
  }

  // Show message
  function showMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = type;
    formMessage.classList.remove("hidden");

    setTimeout(() => {
      formMessage.classList.add("hidden");
    }, 5000);
  }

  // Search and filter
  searchInput.addEventListener("input", fetchStudents);
  gradeFilter.addEventListener("change", fetchStudents);

  // Export to CSV
  exportBtn.addEventListener("click", () => {
    window.location.href = "/students/export/csv";
  });

  // Modal close
  modalClose.addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  window.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.add("hidden");
    }
  });

  // Initialize
  fetchStudents();
});
