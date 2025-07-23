document.addEventListener('DOMContentLoaded', () => {
    const fileDropZone = document.getElementById('file-drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadLink = document.querySelector('.upload-link');

    const placeholderContent = document.getElementById('placeholder-content');
    const outputContent = document.getElementById('output-content');
    const markdownOutput = document.getElementById('markdown-output');
    
    const previewBtn = document.getElementById('preview-btn');
    const downloadBtn = document.getElementById('download-btn');
    const modal = document.getElementById('preview-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const previewContainer = document.getElementById('preview-container');
    const langSwitcher = document.querySelector('.lang-switcher');

    // --- State ---
    let currentLang = 'en';
    let currentTaskId = null;
    let pollingInterval = null;

    // --- API Configuration ---
    const API_BASE_URL = 'https://api.any2md.cc/api/v1/async'; // 根据实际后端地址调整

    // --- Translations ---
    const translations = {
        en: {
            title: "Markdown Converter",
            subtitle: "Supports converting multiple file formats to Markdown documents for easy AI reading and understanding",
            dropZoneText1: "Drag \u0026 drop files here or ",
            dropZoneText2: "click to select",
            maxFileSize: "Maximum file size: 5MB",
            formatsAndUsage: "Formats \u0026 Usage",
            outputPlaceholderTitle: "Output Area",
            outputPlaceholderText: "Upload a supported file from the left panel. The system will automatically convert it to Markdown, and the result will be displayed here.",
            previewButton: "Preview Content",
            downloadButton: "Download File",
            outputHeader: "Conversion Result",
            previewButton2: "Preview Content",
            downloadButton2: "Download File",
            modalTitle: "Content Preview",
            processingFile: "Processing",
            uploadLink: "click to select",
            uploadingFile: "Uploading",
            waitingForProcessing: "Waiting for processing",
            processing: "Processing",
            processingProgress: "Processing progress",
            downloadReady: "Download ready",
            uploadFailed: "Upload failed",
            processingFailed: "Processing failed",
            retry: "Retry",
            extractImages: "Extract images from document"
        },
        zh: {
            title: "Markdown 转换工具",
            subtitle: "支持多种文件格式转换为Markdown文档，方便 AI 进行读取与理解",
            dropZoneText1: "拖拽文件到此处或",
            dropZoneText2: "点击选择",
            maxFileSize: "最大文件大小: 5MB",
            formatsAndUsage: "格式支持与使用说明",
            outputPlaceholderTitle: "转换结果显示区域",
            outputPlaceholderText: "选择左侧支持的文件格式进行上传，系统将自动转换为Markdown格式，处理完成后结果会在此处显示",
            previewButton: "预览内容",
            downloadButton: "下载文件",
            outputHeader: "转换结果",
            previewButton2: "预览内容",
            downloadButton2: "下载文件",
            modalTitle: "内容预览",
            processingFile: "正在处理",
            uploadLink: "点击选择",
            uploadingFile: "正在上传",
            waitingForProcessing: "等待处理",
            processing: "处理中",
            processingProgress: "处理进度",
            downloadReady: "下载就绪",
            uploadFailed: "上传失败",
            processingFailed: "处理失败",
            retry: "重试",
            extractImages: "从文档中提取图片"
        }
    };

    // --- API Functions ---
    const getUploadUrl = async (filename, contentType) => {
        const response = await fetch(`${API_BASE_URL}/upload-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename, content_type: contentType })
        });
        if (!response.ok) throw new Error('Failed to get upload URL');
        return response.json();
    };

    const uploadToMinIO = async (uploadUrl, file) => {
        const response = await fetch(uploadUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': file.type,
            },
            body: file
        });
        if (!response.ok) throw new Error('Failed to upload to MinIO');
        return response;
    };

    const createConversionTask = async (objectName, originalFilename, extractImages = false) => {
        const response = await fetch(`${API_BASE_URL}/create-task`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                object_name: objectName,
                original_filename: originalFilename,
                extract_images: extractImages
            })
        });
        if (!response.ok) throw new Error('Failed to create conversion task');
        return response.json();
    };

    const getTaskStatus = async (taskId) => {
        const response = await fetch(`${API_BASE_URL}/task/${taskId}`);
        if (!response.ok) throw new Error('Failed to get task status');
        return response.json();
    };

    const getDownloadUrl = async (taskId) => {
        const response = await fetch(`${API_BASE_URL}/download/${taskId}`);
        if (!response.ok) throw new Error('Failed to get download URL');
        return response.json();
    };

    // --- UI Functions ---
    const switchLanguage = (lang) => {
        if (!translations[lang] || currentLang === lang) return;
        currentLang = lang;
        document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';

        document.querySelectorAll('[data-lang-key]').forEach(el => {
            const key = el.dataset.langKey;
            if (translations[lang][key]) {
                el.textContent = translations[lang][key];
            }
        });

        langSwitcher.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
    };

    const updateDropZoneState = (state, fileName = '', progress = 0) => {
        const states = {
            idle: () => `
                <div class="upload-icon-container">
                    <i class="fas fa-upload"></i>
                </div>
                <p class="drop-zone-text">
                    <span data-lang-key="dropZoneText1">${translations[currentLang].dropZoneText1}</span>
                    <span class="upload-link" data-lang-key="dropZoneText2">${translations[currentLang].dropZoneText2}</span>
                </p>
                <p class="drop-zone-hint" data-lang-key="maxFileSize">${translations[currentLang].maxFileSize}</p>
                
            `,
            uploading: () => `
                <div class="upload-icon-container">
                    <i class="fas fa-spinner fa-spin"></i>
                </div>
                <p class="drop-zone-text">${translations[currentLang].uploadingFile}: ${fileName}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
            `,
            processing: () => `
                <div class="upload-icon-container">
                    <i class="fas fa-cog fa-spin"></i>
                </div>
                <p class="drop-zone-text">${translations[currentLang].processing}: ${fileName}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
                <p class="drop-zone-hint">${translations[currentLang].processingProgress}: ${progress}%</p>
            `,
            completed: () => `
                <div class="upload-icon-container" style="background: linear-gradient(135deg, #10B981, #059669); color: white;">
                    <i class="fas fa-check"></i>
                </div>
                <p class="drop-zone-text" style="color: #059669; font-weight: 600;">${translations[currentLang].downloadReady}</p>
            `,
            error: () => `
                <div class="upload-icon-container" style="background: linear-gradient(135deg, #EF4444, #dc2626); color: white;">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <p class="drop-zone-text" style="color: #dc2626; font-weight: 600;">${translations[currentLang].uploadFailed}</p>
                <button class="retry-btn" onclick="window.location.reload()">${translations[currentLang].retry}</button>
            `
        };

        fileDropZone.innerHTML = states[state]();
        
        if (state === 'idle') {
            const newUploadLink = fileDropZone.querySelector('.upload-link');
            newUploadLink.addEventListener('click', (e) => {
                e.stopPropagation();
                fileInput.click();
            });
        }
    };

    const handleFile = async (file) => {
        if (!file) return;
        
        // 获取图片提取选项
        const extractImagesCheckbox = document.getElementById('extract-images-checkbox');
        const extractImages = extractImagesCheckbox ? extractImagesCheckbox.checked : false;
        
        try {
            // Step 1: Get upload URL
            updateDropZoneState('uploading', file.name, 0);
            const { upload_url, object_name, file_id } = await getUploadUrl(file.name, file.type);
            
            // Step 2: Upload to MinIO
            await uploadToMinIO(upload_url, file);
            updateDropZoneState('processing', file.name, 0);
            
            // Step 3: Create conversion task
            const taskResponse = await createConversionTask(object_name, file.name, extractImages);
            currentTaskId = taskResponse.task_id;
            
            // Step 4: Poll for status
            startPolling(currentTaskId);
            
        } catch (error) {
            console.error('Upload failed:', error);
            updateDropZoneState('error');
        }
    };

    const startPolling = (taskId) => {
        pollingInterval = setInterval(async () => {
            try {
                const status = await getTaskStatus(taskId);
                
                if (status.status === 'processing') {
                    updateDropZoneState('processing', status.filename, status.progress || 0);
                } else if (status.status === 'completed') {
                    clearInterval(pollingInterval);
                    updateDropZoneState('completed');
                    
                    // Show result
                    placeholderContent.classList.add('hidden');
                    outputContent.classList.remove('hidden');
                    
                    // Try to get download URL and content
                    try {
                        const downloadResponse = await getDownloadUrl(taskId);
                        if (downloadResponse.download_url) {
                            // Fetch the actual markdown content
                            const contentResponse = await fetch(downloadResponse.download_url);
                            if (contentResponse.ok) {
                                const markdownContent = await contentResponse.text();
                                markdownOutput.value = markdownContent;
                                downloadBtn.dataset.downloadUrl = downloadResponse.download_url;
                                downloadBtn.dataset.filename = downloadResponse.filename || `converted-${Date.now()}.md`;
                                
                                // Update character count
                                const fileSizeElement = document.getElementById('file-size');
                                if (fileSizeElement) {
                                    fileSizeElement.textContent = `${markdownContent.length} characters`;
                                }
                            }
                        } else {
                            // Fallback to result data if available
                            const content = status.result?.markdown || '';
                            markdownOutput.value = content;
                            
                            // Update character count
                            const fileSizeElement = document.getElementById('file-size');
                            if (fileSizeElement) {
                                fileSizeElement.textContent = `${content.length} characters`;
                            }
                        }
                    } catch (downloadError) {
                        console.error('Failed to get download URL:', downloadError);
                        const content = status.result?.markdown || '';
                        markdownOutput.value = content;
                        
                        // Update character count
                        const fileSizeElement = document.getElementById('file-size');
                        if (fileSizeElement) {
                            fileSizeElement.textContent = `${content.length} characters`;
                        }
                    }
                    
                } else if (status.status === 'failed') {
                    clearInterval(pollingInterval);
                    updateDropZoneState('error');
                    console.error('Processing failed:', status.error);
                }
            } catch (error) {
                console.error('Polling failed:', error);
                clearInterval(pollingInterval);
                updateDropZoneState('error');
            }
        }, 2000);
    };

    const resetDropZone = () => {
        updateDropZoneState('idle');
        fileDropZone.addEventListener('click', () => fileInput.click());
    };

    const simpleMarkdownToHtml = (markdown) => {
        return markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>')
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');
    };

    // --- Event Listeners ---
    fileDropZone.addEventListener('dragover', (e) => { e.preventDefault(); fileDropZone.classList.add('dragover'); });
    fileDropZone.addEventListener('dragleave', () => fileDropZone.classList.remove('dragover'));
    fileDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => { if (e.target.files.length) handleFile(e.target.files[0]); });

    langSwitcher.addEventListener('click', (e) => {
        const langBtn = e.target.closest('.lang-btn');
        if (langBtn) {
            switchLanguage(langBtn.dataset.lang);
        }
    });

    previewBtn.addEventListener('click', () => {
        previewContainer.innerHTML = simpleMarkdownToHtml(markdownOutput.value);
        modal.classList.remove('hidden');
    });

    closeModalBtn.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.add('hidden'); });
    
    downloadBtn.addEventListener('click', async () => {
        const downloadUrl = downloadBtn.dataset.downloadUrl;
        const filename = downloadBtn.dataset.filename || `converted-${Date.now()}.md`;
        if (!downloadUrl) return;
        
        try {
            const response = await fetch(downloadUrl);
            if (!response.ok) throw new Error('Failed to download file');
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
            alert(currentLang === 'zh' ? '下载失败，请重试' : 'Download failed, please try again');
        }
    });

    // --- Initializer ---
    switchLanguage('en');
    resetDropZone();
});