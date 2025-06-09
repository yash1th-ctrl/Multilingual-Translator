/**
 * Enhanced Audio Upload Functionality
 * Handles drag-and-drop, file validation, metadata extraction, and progress tracking
 */

class EnhancedAudioUpload {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('audioInput');
        this.currentFile = null;
        this.isValidFile = false;
        
        // State elements
        this.defaultState = document.getElementById('defaultState');
        this.dragOverState = document.getElementById('dragOverState');
        this.progressState = document.getElementById('progressState');
        this.previewState = document.getElementById('previewState');
        this.errorState = document.getElementById('errorState');
        
        // Step elements
        this.languageStep = document.getElementById('languageStep');
        this.translateStep = document.getElementById('translateStep');
        this.audioTargetLang = document.getElementById('audioTargetLang');
        this.translateBtn = document.getElementById('translateAudioBtn');
        
        // Progress elements
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        
        // Preview elements
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.fileDuration = document.getElementById('fileDuration');
        this.fileFormat = document.getElementById('fileFormat');
        this.playPreview = document.getElementById('playPreview');
        this.removeFile = document.getElementById('removeFile');
        this.audioPreviewPlayer = document.getElementById('audioPreviewPlayer');
        this.previewAudioSource = document.getElementById('previewAudioSource');
        
        // Error elements
        this.errorMessage = document.getElementById('errorMessage');
        this.retryUpload = document.getElementById('retryUpload');
        
        // Processing elements
        this.processingInfo = document.getElementById('processingInfo');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.resetToDefaultState();
    }
    
    setupEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Click to upload
        this.uploadArea.addEventListener('click', () => {
            if (this.defaultState && !this.defaultState.classList.contains('hidden')) {
                this.fileInput.click();
            }
        });
        
        // Preview controls
        if (this.playPreview) {
            this.playPreview.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleAudioPreview();
            });
        }
        
        if (this.removeFile) {
            this.removeFile.addEventListener('click', (e) => {
                e.stopPropagation();
                this.removeCurrentFile();
            });
        }
        
        // Retry button
        if (this.retryUpload) {
            this.retryUpload.addEventListener('click', () => this.resetToDefaultState());
        }
        
        // Form submission
        const audioForm = document.getElementById('audioForm');
        if (audioForm) {
            audioForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.add('drag-over');
        this.showState('dragOver');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Only remove drag-over if we're leaving the upload area entirely
        if (!this.uploadArea.contains(e.relatedTarget)) {
            this.uploadArea.classList.remove('drag-over');
            if (!this.currentFile) {
                this.showState('default');
            } else {
                this.showState('preview');
            }
        }
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    async processFile(file) {
        this.currentFile = file;
        this.showState('progress');
        this.updateProgress(0, 'Validating file...');
        
        try {
            // Simulate progress for better UX
            await this.simulateProgress();
            
            // Validate file with server
            const validation = await this.validateFile(file);
            
            if (validation.valid) {
                this.isValidFile = true;
                this.showFilePreview(validation);
                this.enableNextSteps();
            } else {
                this.showError(validation.error);
            }
        } catch (error) {
            console.error('File processing error:', error);
            this.showError('Failed to process file. Please try again.');
        }
    }
    
    async simulateProgress() {
        const steps = [
            { progress: 20, text: 'Checking file format...' },
            { progress: 40, text: 'Validating file size...' },
            { progress: 60, text: 'Analyzing audio metadata...' },
            { progress: 80, text: 'Verifying audio quality...' },
            { progress: 100, text: 'Validation complete!' }
        ];
        
        for (const step of steps) {
            this.updateProgress(step.progress, step.text);
            await new Promise(resolve => setTimeout(resolve, 300));
        }
    }
    
    async validateFile(file) {
        const formData = new FormData();
        formData.append('audio', file);
        
        const response = await fetch('/validate-audio', {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    showFilePreview(metadata) {
        this.fileName.textContent = metadata.filename;
        this.fileSize.textContent = `${metadata.size_mb} MB`;
        this.fileDuration.textContent = metadata.duration_formatted;
        this.fileFormat.textContent = metadata.format;
        
        // Create preview URL for audio
        const url = URL.createObjectURL(this.currentFile);
        this.previewAudioSource.src = url;
        
        this.showState('preview');
    }
    
    toggleAudioPreview() {
        if (this.audioPreviewPlayer.classList.contains('hidden')) {
            this.audioPreviewPlayer.classList.remove('hidden');
            this.playPreview.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            this.audioPreviewPlayer.classList.add('hidden');
            this.playPreview.innerHTML = '<i class="fas fa-play"></i>';
            const audio = this.audioPreviewPlayer.querySelector('audio');
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
        }
    }
    
    removeCurrentFile() {
        this.currentFile = null;
        this.isValidFile = false;
        this.fileInput.value = '';
        
        // Clean up preview URL
        if (this.previewAudioSource.src) {
            URL.revokeObjectURL(this.previewAudioSource.src);
            this.previewAudioSource.src = '';
        }
        
        this.resetToDefaultState();
        this.disableNextSteps();
    }
    
    enableNextSteps() {
        // Enable language selection step
        this.languageStep.style.opacity = '1';
        this.languageStep.style.pointerEvents = 'auto';
        this.audioTargetLang.disabled = false;
        
        const stepStatus = this.languageStep.querySelector('.step-status');
        if (stepStatus) {
            stepStatus.innerHTML = '<i class="fas fa-check"></i><small>Ready to select</small>';
        }
        
        // Enable translate step
        this.translateStep.style.opacity = '1';
        this.translateStep.style.pointerEvents = 'auto';
        this.translateBtn.disabled = false;
        
        const translateStepStatus = this.translateStep.querySelector('.step-status');
        if (translateStepStatus) {
            translateStepStatus.innerHTML = '<i class="fas fa-check"></i><small>Ready to translate</small>';
        }
    }
    
    disableNextSteps() {
        // Disable language selection step
        this.languageStep.style.opacity = '0.5';
        this.languageStep.style.pointerEvents = 'none';
        this.audioTargetLang.disabled = true;
        
        const stepStatus = this.languageStep.querySelector('.step-status');
        if (stepStatus) {
            stepStatus.innerHTML = '<i class="fas fa-lock"></i><small>Upload audio file first</small>';
        }
        
        // Disable translate step
        this.translateStep.style.opacity = '0.5';
        this.translateStep.style.pointerEvents = 'none';
        this.translateBtn.disabled = true;
        
        const translateStepStatus = this.translateStep.querySelector('.step-status');
        if (translateStepStatus) {
            translateStepStatus.innerHTML = '<i class="fas fa-lock"></i><small>Complete previous steps</small>';
        }
    }
    
    showState(state) {
        // Hide all states
        [this.defaultState, this.dragOverState, this.progressState, this.previewState, this.errorState].forEach(el => {
            if (el) el.classList.add('hidden');
        });
        
        // Show requested state
        switch (state) {
            case 'default':
                if (this.defaultState) this.defaultState.classList.remove('hidden');
                break;
            case 'dragOver':
                if (this.dragOverState) this.dragOverState.classList.remove('hidden');
                break;
            case 'progress':
                if (this.progressState) this.progressState.classList.remove('hidden');
                break;
            case 'preview':
                if (this.previewState) this.previewState.classList.remove('hidden');
                break;
            case 'error':
                if (this.errorState) this.errorState.classList.remove('hidden');
                break;
        }
    }
    
    updateProgress(percentage, text) {
        if (this.progressFill) {
            this.progressFill.style.width = `${percentage}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = `${percentage}%`;
        }
        if (text && this.progressState) {
            const h5 = this.progressState.querySelector('h5');
            if (h5) h5.textContent = text;
        }
    }
    
    showError(message) {
        if (this.errorMessage) {
            this.errorMessage.textContent = message;
        }
        this.showState('error');
        this.isValidFile = false;
        this.disableNextSteps();
    }
    
    resetToDefaultState() {
        this.showState('default');
        this.uploadArea.classList.remove('drag-over');
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.isValidFile || !this.currentFile) {
            alert('Please upload a valid audio file first.');
            return;
        }
        
        const targetLang = this.audioTargetLang.value;
        if (!targetLang) {
            alert('Please select a target language.');
            return;
        }
        
        // Show processing state
        this.showProcessingSteps();
        
        try {
            const formData = new FormData();
            formData.append('audio', this.currentFile);
            formData.append('target_lang', targetLang);
            
            const response = await fetch('/translate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.hideProcessingSteps();
                this.showTranslationResults(data);
            } else {
                this.hideProcessingSteps();
                alert(data.error || 'Translation failed');
            }
        } catch (error) {
            this.hideProcessingSteps();
            console.error('Translation error:', error);
            alert('An error occurred during translation');
        }
    }
    
    showProcessingSteps() {
        if (this.processingInfo) {
            this.processingInfo.classList.remove('hidden');
        }
        
        // Show button loading state
        const btnText = this.translateBtn.querySelector('.btn-text');
        const btnLoading = this.translateBtn.querySelector('.btn-loading');
        if (btnText) btnText.classList.add('hidden');
        if (btnLoading) btnLoading.classList.remove('hidden');
        
        this.translateBtn.disabled = true;
        
        // Animate processing steps
        this.animateProcessingSteps();
    }
    
    hideProcessingSteps() {
        if (this.processingInfo) {
            this.processingInfo.classList.add('hidden');
        }
        
        // Hide button loading state
        const btnText = this.translateBtn.querySelector('.btn-text');
        const btnLoading = this.translateBtn.querySelector('.btn-loading');
        if (btnText) btnText.classList.remove('hidden');
        if (btnLoading) btnLoading.classList.add('hidden');
        
        this.translateBtn.disabled = false;
    }
    
    async animateProcessingSteps() {
        const steps = this.processingInfo.querySelectorAll('.processing-step');
        
        for (let i = 0; i < steps.length; i++) {
            steps[i].classList.add('active');
            await new Promise(resolve => setTimeout(resolve, 1500));
            if (i < steps.length - 1) {
                steps[i].classList.remove('active');
            }
        }
    }
    
    showTranslationResults(data) {
        // Use existing results display functionality
        if (window.showTranslationResults) {
            window.showTranslationResults(data);
        } else {
            // Fallback display
            const results = document.getElementById('results');
            if (results) {
                document.getElementById('originalText').textContent = data.original_text;
                document.getElementById('translatedText').textContent = data.translated_text;
                
                if (data.audio_url) {
                    const audioPlayer = document.getElementById('audioPlayer');
                    const audioSource = document.getElementById('audioSource');
                    audioSource.src = data.audio_url;
                    audioPlayer.style.display = 'block';
                    audioSource.parentElement.load();
                }
                
                results.style.display = 'block';
                results.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
}

// Initialize enhanced audio upload when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('uploadArea')) {
        new EnhancedAudioUpload();
    }
});
