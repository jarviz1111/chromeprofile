/**
 * Browser Session Manager - Client-side JavaScript
 * Handles UI interactions and communication with the server
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const apiUserIdInput = document.getElementById('apiUserId');
  const apiKeyIdInput = document.getElementById('apiKeyId');
  const csvFileInput = document.getElementById('csvFile');
  const fileNameDisplay = document.getElementById('fileNameDisplay');
  const globalProxyInput = document.getElementById('globalProxy');
  const startProcessingBtn = document.getElementById('startProcessingBtn');
  const nextProfileBtn = document.getElementById('nextProfileBtn');
  const consoleElement = document.getElementById('console');
  const progressSection = document.getElementById('progressSection');
  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');
  const currentProfileText = document.getElementById('currentProfileText');
  const deleteProfileButtons = document.querySelectorAll('.delete-profile');
  
  // State variables
  let isProcessing = false;
  let totalProfiles = 0;
  let currentProfileIndex = 0;
  
  // Browse button functionality
  const browseButton = document.getElementById('browseButton');
  
  // Event listeners
  csvFileInput.addEventListener('change', handleFileChange);
  startProcessingBtn.addEventListener('click', startProcessing);
  nextProfileBtn.addEventListener('click', processNextProfile);
  
  // Trigger file input when browse button is clicked
  if (browseButton) {
    browseButton.addEventListener('click', function() {
      csvFileInput.click();
    });
  }
  
  // Setup delete profile buttons
  deleteProfileButtons.forEach(button => {
    button.addEventListener('click', function() {
      const profileId = this.getAttribute('data-profile-id');
      deleteProfile(profileId);
    });
  });
  
  /**
   * Display a message in the console
   * @param {string} message - Message to display
   * @param {string} type - Message type (info, success, error, warning)
   */
  function logToConsole(message, type = 'info') {
    const timestampStr = new Date().toLocaleTimeString();
    let prefix = '';
    
    switch (type) {
      case 'success':
        prefix = '✅ ';
        break;
      case 'error':
        prefix = '❌ ';
        break;
      case 'warning':
        prefix = '⚠️ ';
        break;
      case 'info':
      default:
        prefix = '🔹 ';
        break;
    }
    
    const logMessage = `[${timestampStr}] ${prefix}${message}`;
    const messageElement = document.createElement('div');
    messageElement.textContent = logMessage;
    messageElement.classList.add(`log-${type}`);
    
    consoleElement.appendChild(messageElement);
    consoleElement.scrollTop = consoleElement.scrollHeight;
  }
  
  /**
   * Handle file selection change
   */
  function handleFileChange() {
    if (csvFileInput.files.length > 0) {
      fileNameDisplay.textContent = csvFileInput.files[0].name;
    } else {
      fileNameDisplay.textContent = 'No file selected';
    }
  }
  
  /**
   * Verify API credentials
   * @returns {Promise<boolean>} True if verification passed, false otherwise
   */
  async function verifyApiCredentials() {
    const apiUserId = apiUserIdInput.value.trim();
    const apiKeyId = apiKeyIdInput.value.trim();
    
    if (!apiUserId || !apiKeyId) {
      logToConsole('API credentials are required', 'error');
      return false;
    }
    
    logToConsole('Verifying API credentials...');
    
    try {
      const response = await fetch('/verify-api', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ apiUserId, apiKeyId })
      });
      
      const data = await response.json();
      
      if (data.success) {
        logToConsole('API credentials verified', 'success');
        return true;
      } else {
        logToConsole(`API verification failed: ${data.message}`, 'error');
        return false;
      }
    } catch (error) {
      logToConsole(`API verification error: ${error.message}`, 'error');
      return false;
    }
  }
  
  /**
   * Upload CSV file and get profile list
   * @returns {Promise<boolean>} True if upload was successful, false otherwise
   */
  async function uploadCsvFile() {
    if (!csvFileInput.files.length) {
      logToConsole('Please select a CSV file', 'error');
      return false;
    }
    
    const formData = new FormData();
    formData.append('csvFile', csvFileInput.files[0]);
    formData.append('globalProxy', globalProxyInput.value.trim());
    
    logToConsole('Uploading and processing CSV file...');
    
    try {
      const response = await fetch('/upload-csv', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (data.success) {
        logToConsole(data.message, 'success');
        totalProfiles = data.profiles.length;
        updateProgressBar(0, totalProfiles);
        return true;
      } else {
        logToConsole(`CSV upload failed: ${data.message}`, 'error');
        return false;
      }
    } catch (error) {
      logToConsole(`CSV upload error: ${error.message}`, 'error');
      return false;
    }
  }
  
  /**
   * Start processing profiles
   */
  async function startProcessing() {
    if (isProcessing) {
      logToConsole('Processing is already in progress', 'warning');
      return;
    }
    
    // Verify API credentials
    if (!await verifyApiCredentials()) {
      return;
    }
    
    // Upload and process CSV
    if (!await uploadCsvFile()) {
      return;
    }
    
    try {
      const response = await fetch('/start-processing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      
      const data = await response.json();
      
      if (data.success) {
        isProcessing = true;
        currentProfileIndex = 0;
        progressSection.style.display = 'block';
        logToConsole('Processing started', 'success');
        
        // Process first profile automatically
        processNextProfile();
      } else {
        logToConsole(`Failed to start processing: ${data.message}`, 'error');
      }
    } catch (error) {
      logToConsole(`Error starting process: ${error.message}`, 'error');
    }
  }
  
  /**
   * Process the next profile
   */
  async function processNextProfile() {
    if (!isProcessing && currentProfileIndex === 0) {
      logToConsole('Please start processing first', 'warning');
      return;
    }
    
    logToConsole('Processing next profile...');
    
    try {
      const response = await fetch('/process-next', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      
      const data = await response.json();
      
      if (data.success) {
        if (data.complete) {
          // All profiles processed
          logToConsole('All profiles processed!', 'success');
          logToConsole('Browser Session Manager has completed processing all profiles.', 'success');
          isProcessing = false;
          updateProgressBar(totalProfiles, totalProfiles);
          currentProfileText.textContent = 'Complete';
        } else {
          // Profile processed successfully
          currentProfileIndex = data.progress.current;
          updateProgressBar(currentProfileIndex, data.progress.total);
          
          logToConsole(`Started profile: ${data.currentProfile.profileId}`, 'success');
          currentProfileText.textContent = `Current profile: ${data.currentProfile.profileId}`;
          
          if (data.currentProfile.proxy) {
            logToConsole(`Using proxy: ${data.currentProfile.proxy}`);
          } else {
            logToConsole('No proxy being used for this profile');
          }
        }
      } else {
        // Error processing profile
        logToConsole(data.message, 'error');
        
        if (data.nextAvailable) {
          const proceed = confirm('Failed to process profile. Do you want to skip to the next one?');
          if (proceed) {
            processNextProfile();
          }
        } else {
          logToConsole('No more profiles to process.', 'warning');
          isProcessing = false;
        }
      }
    } catch (error) {
      logToConsole(`Error processing profile: ${error.message}`, 'error');
    }
  }
  
  /**
   * Update the progress bar
   * @param {number} current - Current progress
   * @param {number} total - Total items
   */
  function updateProgressBar(current, total) {
    const percentage = total > 0 ? (current / total) * 100 : 0;
    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${current}/${total} profiles processed`;
  }
  
  /**
   * Delete a profile
   * @param {string} profileId - Profile ID to delete
   */
  async function deleteProfile(profileId) {
    if (!confirm(`Are you sure you want to delete profile "${profileId}"?`)) {
      return;
    }
    
    try {
      const response = await fetch('/delete-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ profileId })
      });
      
      const data = await response.json();
      
      if (data.success) {
        logToConsole(data.message, 'success');
        // Reload page to refresh profile list
        window.location.reload();
      } else {
        logToConsole(`Failed to delete profile: ${data.message}`, 'error');
      }
    } catch (error) {
      logToConsole(`Error deleting profile: ${error.message}`, 'error');
    }
  }
  
  // Initial console message
  logToConsole('🚀 Browser Session Manager started.');
  logToConsole('Please select a CSV file with profiles and enter your API credentials.');
});