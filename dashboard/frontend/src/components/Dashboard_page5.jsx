import React, { useState, useEffect, useRef } from 'react';
import AiService from './ai/AiService';
import AiHistoryPanel from './ai/AiHistoryPanel';
import AiRequestForm from './ai/AiRequestForm';
import AiChatMessage from './ai/AiChatMessage';
import { Sparkles } from 'lucide-react';

// Sinh 1 ID cuộc hội thoại mới (ưu tiên crypto.randomUUID, fallback timestamp)
const newConversationId = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : 'conv_' + Date.now();

// A5c: nhận diện lỗi HẾT QUOTA/rate-limit từ thông báo lỗi thô của Google API —
// cùng logic với backend (ai_config.py: is_quota_error kiểm "429"/"quota"/
// "ResourceExhausted"), để hiện thông báo thân thiện + nút Thử lại thay vì chuỗi
// lỗi kỹ thuật gốc.
const isQuotaError = (message) => /429|quota|resourceexhausted/i.test(message || '');

// Vài câu hỏi mẫu để bấm bắt đầu ngay ở màn hình chào (chat rỗng) — chọn đại
// diện cho các dạng câu hỏi khác nhau (nhận xét văn bản, so sánh, vẽ biểu đồ).
const WELCOME_STARTERS = [
  'Top 15 kỹ năng công nghệ được săn đón nhiều nhất trong ngành IT là gì?',
  'So sánh mức lương giữa Senior và Junior/Fresher',
  'Vẽ biểu đồ số lượng tin tuyển dụng theo nhóm vị trí',
  'Xu hướng làm việc từ xa thay đổi thế nào theo thời gian?'
];

export default function Dashboard_page5() {
  const [historyList, setHistoryList] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(() => newConversationId());
  const [messages, setMessages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [executingId, setExecutingId] = useState(null);
  // Tự động nhận xét sau khi 1 biểu đồ chạy thành công (tách 2 pha: biểu đồ hiện
  // ngay, nhận xét đến sau) — mặc định bật, người dùng có thể tắt để tiết kiệm quota.
  const [autoComment, setAutoComment] = useState(true);
  const messagesEndRef = useRef(null);
  // A2a: AbortController của lượt stream đang chạy — bấm nút Dừng sẽ abort fetch,
  // backend (StreamingResponse) cũng ngừng generator theo, không tốn thêm quota.
  const abortRef = useRef(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    // Auto scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const data = await AiService.getHistory();
      setHistoryList(data);
    } catch (error) {
      console.error('Failed to load history', error);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentConversationId(newConversationId());
    setIsSubmitting(false);
    setExecutingId(null);
  };

  // Gửi 1 yêu cầu và nhận câu trả lời theo THỜI GIAN THỰC (streaming SSE).
  // mode: null/'auto' (mặc định) | 'ask' (/hoi) | 'code' (/code) | 'explain' (/giaithich) | 'comment' (/nhanxet)
  // catalogHint (A3): mã danh mục đã biết trước (từ chip gợi ý) — xem handleResend.
  const handleSendRequest = (prompt, image, mode, catalogHint) => {
    const tempId = 'tmp_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);

    const userMsg = {
      id: tempId + '_user',
      role: 'user',
      content: prompt,
      image: image || null,
      timestamp: new Date().toISOString()
    };
    const loadingMsg = {
      id: tempId + '_loading',
      role: 'loading',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setIsSubmitting(true);

    let textStarted = false;
    // A2a: mỗi lượt gửi tạo 1 AbortController mới để nút Dừng hủy đúng lượt này.
    const controller = new AbortController();
    abortRef.current = controller;

    AiService.streamRequest(
      { prompt, conversationId: currentConversationId, image, mode, catalogHint, signal: controller.signal },
      {
        onStart: (meta) => {
          // Mẫu 6: MỌI nhánh giờ đều stream văn bản ngay từ đầu (kể cả nhánh có
          // thể ra code — Chế độ B luôn viết dẫn nhập + "Hướng phân tích" trước
          // code) nên luôn tạo bong bóng văn bản streaming; nếu cuối cùng ra code,
          // onDone sẽ chuyển bong bóng này thành ai_code (giữ lại phần dẫn nhập).
          textStarted = true;
          setMessages(prev => prev.filter(m => m.id !== tempId + '_loading').concat({
            id: tempId + '_text',
            role: 'ai_text',
            content: '',
            prompt,
            requestId: null,
            streaming: true,
            // Mẫu 5: nếu câu hỏi trúng 1 mục trong danh mục biểu đồ, backend gửi
            // kèm figure THẬT ngay từ đầu — AiChatMessage sẽ chèn nó vào đúng vị
            // trí marker [[BIEU_DO]] khi nội dung stream chảy tới đó.
            catalogId: meta.catalogId || null,
            figure: meta.figure || null,
            timestamp: new Date().toISOString()
          }));
        },
        onDelta: (text) => {
          if (!textStarted) return;
          setMessages(prev => prev.map(m =>
            m.id === tempId + '_text' ? { ...m, content: (m.content || '') + text } : m
          ));
        },
        onDone: (meta) => {
          setIsSubmitting(false);
          if (meta.type === 'text') {
            setMessages(prev => prev.map(m =>
              m.id === tempId + '_text'
                ? {
                    ...m, id: meta.requestId + '_text', requestId: meta.requestId,
                    streaming: false, suggestions: meta.suggestions || []
                  }
                : m
            ));
          } else {
            // type === 'code' (Mẫu 6): bong bóng văn bản đang stream (dẫn nhập +
            // Hướng phân tích + code thô) được thay bằng bong bóng ai_code chính
            // thức, giữ lại preamble để hiển thị phía trên khung code duyệt/chạy.
            setMessages(prev => prev
              .filter(m => m.id !== tempId + '_loading' && m.id !== tempId + '_text')
              .concat({
                id: meta.requestId + '_code',
                // turnId = chính id của bong bóng này — dùng làm "mỏ neo" gộp
                // khung với kết quả chạy (ai_result) + nhận xét tự động (ai_text)
                // của CÙNG lượt hỏi này thành 1 khung duy nhất (.ai-turn-card ở
                // dưới). Ổn định qua các lần Tạo lại/Tinh chỉnh (A2b) vì đó chỉ
                // đổi requestId/code, không đổi id của chính bong bóng.
                turnId: meta.requestId + '_code',
                role: 'ai_code',
                code: meta.code,
                preamble: meta.preamble || '',
                prompt,
                status: 'pending_approval',
                requestId: meta.requestId,
                timestamp: new Date().toISOString()
              }));
          }
          fetchHistory();
        },
        // A5c: phân biệt lỗi hết quota (tạm thời, không phải lỗi code) để hiện
        // thông báo thân thiện + nút Thử lại thay vì chuỗi lỗi API thô.
        onError: (message) => {
          setIsSubmitting(false);
          const quota = isQuotaError(message);
          setMessages(prev => prev
            .filter(m => m.id !== tempId + '_loading' && m.id !== tempId + '_text')
            .concat({
              id: tempId + '_error',
              role: 'ai_result',
              resultData: {
                type: 'error',
                kind: quota ? 'quota' : 'api',
                data: quota ? message : 'Lỗi khi gọi API AI: ' + message,
                retry: quota ? { type: 'send', prompt, image, mode, catalogHint } : null
              },
              timestamp: new Date().toISOString()
            }));
        },
        // A2a: người dùng bấm Dừng — giữ lại phần văn bản đã nhận (đánh dấu đã dừng
        // để hiện ghi chú), hoặc gỡ hẳn bong bóng nếu chưa nhận được chữ nào.
        onAbort: () => {
          setIsSubmitting(false);
          setMessages(prev => prev
            .filter(m => m.id !== tempId + '_loading')
            .map(m => m.id === tempId + '_text'
              ? { ...m, streaming: false, stopped: true }
              : m)
            .filter(m => !(m.id === tempId + '_text' && !(m.content || '').trim())));
        }
      }
    );
  };

  // A2a: dừng lượt sinh đang chạy. Lưu ý: backend chỉ lưu lịch sử SAU khi stream
  // trọn vẹn, nên lượt bị dừng sẽ không xuất hiện trong lịch sử — chấp nhận được,
  // vì người dùng đã chủ động bỏ câu trả lời đó.
  const handleStopGenerating = () => {
    abortRef.current?.abort();
  };

  // Tự động nhận xét sau khi 1 biểu đồ chạy thành công — dùng lại đúng lệnh /nhanxet
  // ở phía backend (mode='comment'), backend tự tìm kết quả biểu đồ mới nhất của
  // cuộc hội thoại này. Hiện dạng bong bóng văn bản streaming ngay dưới biểu đồ.
  // turnId: gắn cùng mã neo với code/kết quả phía trên để 3 phần gộp chung 1 khung.
  const triggerAutoComment = (afterRequestId, turnId) => {
    const tempId = 'cmt_' + afterRequestId;
    setMessages(prev => [...prev, {
      id: tempId,
      role: 'ai_text',
      turnId,
      content: '',
      streaming: true,
      isComment: true,
      timestamp: new Date().toISOString()
    }]);

    AiService.streamRequest(
      { prompt: '', conversationId: currentConversationId, mode: 'comment' },
      {
        onDelta: (text) => {
          setMessages(prev => prev.map(m =>
            m.id === tempId ? { ...m, content: (m.content || '') + text } : m
          ));
        },
        onDone: (meta) => {
          setMessages(prev => prev.map(m =>
            m.id === tempId
              ? {
                  ...m, id: meta.requestId + '_comment', requestId: meta.requestId,
                  streaming: false, suggestions: meta.suggestions || []
                }
              : m
          ));
          fetchHistory();
        },
        onError: () => {
          setMessages(prev => prev.map(m =>
            m.id === tempId
              ? { ...m, streaming: false, commentError: true, content: 'Không thể tạo nhận xét tự động.' }
              : m
          ));
        }
      }
    );
  };

  const handleApprove = async (requestId, editedCode) => {
    setExecutingId(requestId);

    // Update code message status to executing — đồng thời lấy turnId (= chính
    // id của bong bóng code) để gắn vào kết quả/nhận xét sắp tạo, gộp chung 1 khung.
    let turnId = null;
    setMessages(prev => prev.map(m => {
      if (m.requestId === requestId && m.role === 'ai_code') {
        turnId = m.turnId || m.id;
        return { ...m, status: 'executing', code: editedCode };
      }
      return m;
    }));

    try {
      const response = await AiService.executeCode(requestId, editedCode);
      const newStatus = response.status === 'success' ? 'success' : 'error';

      // Update code message status
      setMessages(prev => prev.map(m =>
        m.requestId === requestId && m.role === 'ai_code'
          ? { ...m, status: newStatus }
          : m
      ));

      // Add result message
      const resultMsg = {
        id: requestId + '_result',
        role: 'ai_result',
        turnId,
        resultData: response.result || { type: 'error', data: response.logs },
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, resultMsg]);
      fetchHistory();

      // Tách 2 pha: biểu đồ đã hiện xong ở trên — nếu bật tự động nhận xét và có
      // dữ liệu (result.csv) thì mới gọi tiếp, không làm chậm việc hiện biểu đồ.
      if (autoComment && response.result?.type === 'plotly' && response.result?.csv) {
        triggerAutoComment(requestId, turnId);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => prev.map(m =>
        m.requestId === requestId && m.role === 'ai_code'
          ? { ...m, status: 'error' }
          : m
      ));

      const errorMsg = {
        id: requestId + '_result',
        role: 'ai_result',
        turnId,
        resultData: { type: 'error', data: 'Lỗi khi thực thi: ' + error.message },
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
      fetchHistory();
    } finally {
      setExecutingId(null);
    }
  };

  const handleReject = (requestId) => {
    setMessages(prev => prev.map(m =>
      m.requestId === requestId && m.role === 'ai_code'
        ? { ...m, status: 'rejected' }
        : m
    ));
  };

  // Dựng lại toàn bộ tin nhắn của 1 cuộc hội thoại (nhiều câu hỏi nối tiếp nhau).
  // conversation.items đã được sắp xếp tăng dần theo thời gian ở History Panel.
  const handleSelectConversation = (conversation) => {
    setCurrentConversationId(conversation.conversationId);
    const rebuilt = [];
    conversation.items.forEach(item => {
      rebuilt.push({
        id: item.id + '_user',
        role: 'user',
        content: item.prompt,
        image: item.image || null,
        timestamp: item.timestamp
      });
      if (item.type === 'text') {
        rebuilt.push({
          id: item.id + '_text',
          role: 'ai_text',
          content: item.answer,
          prompt: item.prompt,
          requestId: item.id,
          catalogId: item.catalogId || null,
          figure: item.figure || null,
          suggestions: item.suggestions || [],
          timestamp: item.timestamp
        });
      } else if (item.code) {
        rebuilt.push({
          id: item.id + '_code',
          role: 'ai_code',
          code: item.code,
          preamble: item.preamble || '',
          prompt: item.prompt,
          status: item.status || 'success',
          requestId: item.id,
          timestamp: item.timestamp
        });
        if (item.result) {
          rebuilt.push({
            id: item.id + '_result',
            role: 'ai_result',
            resultData: item.result,
            timestamp: item.timestamp
          });
        }
      }
    });
    setMessages(rebuilt);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await AiService.deleteConversation(conversationId);
      // Nếu đang xem đúng cuộc hội thoại vừa xóa thì dọn khung chat về trạng thái mới
      if (conversationId === currentConversationId) {
        handleNewChat();
      }
      fetchHistory();
    } catch (error) {
      console.error('Failed to delete conversation', error);
    }
  };

  const handleTogglePin = async (conversationId) => {
    try {
      await AiService.togglePin(conversationId);
      fetchHistory();
    } catch (error) {
      console.error('Failed to toggle pin', error);
    }
  };

  const handleRenameConversation = async (conversationId, newTitle) => {
    try {
      await AiService.renameConversation(conversationId, newTitle);
      fetchHistory();
    } catch (error) {
      console.error('Failed to rename conversation', error);
    }
  };

  // Tạo lại / Sửa & gửi lại: đều gửi 1 câu hỏi mới trong cùng cuộc hội thoại hiện tại
  // (nhờ ngữ cảnh, AI vẫn hiểu mạch hội thoại). Dùng chung handleSendRequest.
  // catalogHint (A3): khi gọi từ 1 chip gợi ý (AiChatMessage truyền kèm s.id), biết
  // trước câu hỏi ứng với mã nào — cho phép backend bỏ qua bước định tuyến.
  // editingUserMsgId: CHỈ có khi gọi từ nút "Sửa & gửi lại" trên chính bong
  // bóng câu hỏi cũ — nghĩa là người dùng muốn SỬA lượt hỏi đó, không phải hỏi
  // thêm 1 câu mới. Trước đây luôn nối thêm bong bóng mới ở cuối, gây trùng lặp
  // y hệt câu cũ khi không đổi nội dung; giờ xóa bong bóng câu hỏi cũ + mọi bong
  // bóng trả lời/kết quả phía sau nó rồi mới gửi lại, giống hành vi "Edit" của
  // ChatGPT/Gemini (1 bong bóng câu hỏi cho 1 lượt).
  const handleResend = (prompt, catalogHint, editingUserMsgId) => {
    if (prompt && prompt.trim() && !isSubmitting) {
      if (editingUserMsgId) {
        setMessages(prev => {
          const idx = prev.findIndex(m => m.id === editingUserMsgId);
          return idx >= 0 ? prev.slice(0, idx) : prev;
        });
      }
      handleSendRequest(prompt.trim(), null, null, catalogHint);
    }
  };

  // A5c: nút "Thử lại" trên thông báo lỗi hết quota — điều phối lại đúng loại yêu
  // cầu đã thất bại (gửi câu hỏi thường, hay Tạo lại/Tinh chỉnh code/văn bản).
  const handleRetryRequest = (retry) => {
    if (!retry || isSubmitting) return;
    if (retry.type === 'regenerate') {
      handleRegenerateCode(retry.message, retry.refineInstruction);
    } else if (retry.type === 'regenerateText') {
      handleRegenerateText(retry.message);
    } else {
      handleSendRequest(retry.prompt, retry.image, retry.mode, retry.catalogHint);
    }
  };

  // Tạo lại câu trả lời VĂN BẢN (Mẫu 5/nhận xét tự động) TẠI CHỖ — cùng cơ chế
  // priorVersions/‹ i/N › như handleRegenerateCode, nhưng cho bong bóng ai_text:
  // không tạo thêm cặp câu hỏi/trả lời mới, chỉ ghi đè nội dung/biểu đồ/gợi ý
  // của CHÍNH bong bóng này bằng 1 lượt gọi lại (giữ nguyên prompt/mode/catalogHint
  // gốc để có cùng chủ đề). Tái dùng streaming thật (onStart/onDelta/onDone) nên
  // UI "đang trả lời..." hiện lại y hệt lúc trả lời lần đầu.
  const handleRegenerateText = (message) => {
    if (isSubmitting) return;
    const targetId = message.id;

    setMessages(prev => prev.map(m => m.id === targetId ? {
      ...m,
      priorVersions: [...(m.priorVersions || []), {
        content: m.content, figure: m.figure || null, suggestions: m.suggestions || []
      }],
      content: '',
      figure: null,
      suggestions: [],
      streaming: true,
      requestId: null
    } : m));
    setIsSubmitting(true);

    const controller = new AbortController();
    abortRef.current = controller;
    const mode = message.isComment ? 'comment' : null;

    const rollback = () => {
      setMessages(prev => prev.map(m => {
        if (m.id !== targetId) return m;
        const prior = (m.priorVersions || []).slice();
        const last = prior.pop();
        return last
          ? { ...m, content: last.content, figure: last.figure, suggestions: last.suggestions, priorVersions: prior, streaming: false }
          : { ...m, streaming: false };
      }));
    };

    AiService.streamRequest(
      { prompt: message.prompt || '', conversationId: currentConversationId, mode, catalogHint: message.catalogId || null, signal: controller.signal },
      {
        onStart: (meta) => {
          setMessages(prev => prev.map(m => m.id === targetId
            ? { ...m, figure: meta.figure || null, catalogId: meta.catalogId || m.catalogId || null }
            : m));
        },
        onDelta: (text) => {
          setMessages(prev => prev.map(m => m.id === targetId ? { ...m, content: (m.content || '') + text } : m));
        },
        onDone: (meta) => {
          setIsSubmitting(false);
          if (meta.type !== 'text') {
            rollback();
            return;
          }
          setMessages(prev => prev.map(m => m.id === targetId ? {
            ...m, streaming: false, requestId: meta.requestId, suggestions: meta.suggestions || []
          } : m));
          fetchHistory();
        },
        onError: (errMsg) => {
          setIsSubmitting(false);
          rollback();
          const quota = isQuotaError(errMsg);
          setMessages(prev => [...prev, {
            id: targetId + '_regentextfail_' + Date.now(),
            role: 'ai_result',
            resultData: {
              type: 'error',
              kind: quota ? 'quota' : 'api',
              data: quota ? errMsg : 'Lỗi khi tạo lại câu trả lời: ' + errMsg,
              retry: quota ? { type: 'regenerateText', message } : null
            },
            timestamp: new Date().toISOString()
          }]);
        },
        onAbort: () => {
          setIsSubmitting(false);
          rollback();
        }
      }
    );
  };

  // A2b: Tạo lại/Tinh chỉnh code TẠI CHỖ (không tạo bong bóng mới) — thay cho hành
  // vi cũ "Tạo lại" gửi lại y hệt prompt như 1 câu hỏi mới, gây trùng lặp confusing
  // trong luồng chat. Phiên bản hiện tại được đẩy vào priorVersions để xem lại
  // (kiểu "‹ i/N ›"), rồi ô code được ghi đè bằng phiên bản mới sinh ra.
  // refineInstruction rỗng = "Tạo lại" mù (viết code mới từ đầu theo đúng câu hỏi
  // gốc); có nội dung = "Tinh chỉnh" (gửi kèm code hiện tại + yêu cầu chỉnh sửa,
  // theo đúng cơ chế VizOps Refine của LIDA — sửa dựa trên code cũ, không viết lại
  // mù từ đầu).
  const handleRegenerateCode = (message, refineInstruction) => {
    if (isSubmitting) return;
    const targetId = message.id;

    setMessages(prev => prev.map(m => m.id === targetId ? {
      ...m,
      priorVersions: [...(m.priorVersions || []), {
        requestId: m.requestId, code: m.code, preamble: m.preamble || ''
      }],
      // Xóa trắng dẫn nhập/code cũ ngay khi bấm Tạo lại/Tinh chỉnh (giống cách
      // các AI khác dọn sạch để soạn lại từ đầu), thay vì vẫn hiện y hệt nội
      // dung cũ trong lúc chờ — chỉ còn khung "đang soạn" (loading dots).
      preamble: '',
      code: '',
      status: 'generating'
    } : m));
    setIsSubmitting(true);

    const trimmedInstruction = (refineInstruction || '').trim();
    const promptToSend = trimmedInstruction
      ? `${message.prompt}\n\nYêu cầu chỉnh sửa thêm: ${trimmedInstruction}\n\nĐây là code hiện tại, hãy CHỈNH SỬA dựa trên yêu cầu trên (giữ nguyên phần còn phù hợp, không cần viết lại từ đầu nếu không cần thiết):\n\`\`\`python\n${message.code}\n\`\`\``
      : message.prompt;

    const controller = new AbortController();
    abortRef.current = controller;

    // Khôi phục về phiên bản trước đó (trước khi bấm Tạo lại/Tinh chỉnh) khi lượt
    // sinh mới thất bại/bị hủy — không để bong bóng kẹt ở trạng thái "generating".
    const rollback = () => {
      setMessages(prev => prev.map(m => {
        if (m.id !== targetId) return m;
        const prior = (m.priorVersions || []).slice();
        const last = prior.pop();
        return last
          ? { ...m, code: last.code, preamble: last.preamble, requestId: last.requestId, priorVersions: prior, status: 'pending_approval' }
          : { ...m, status: 'pending_approval' };
      }));
    };

    AiService.streamRequest(
      { prompt: promptToSend, conversationId: currentConversationId, mode: 'code', signal: controller.signal },
      {
        onDone: (meta) => {
          setIsSubmitting(false);
          if (meta.type !== 'code' || !meta.code) {
            rollback();
            return;
          }
          setMessages(prev => prev.map(m => m.id === targetId ? {
            ...m,
            code: meta.code,
            preamble: meta.preamble || '',
            status: 'pending_approval',
            requestId: meta.requestId
          } : m));
          fetchHistory();
        },
        // A5c: cũng phân biệt lỗi quota khi Tạo lại/Tinh chỉnh thất bại, kèm nút
        // Thử lại (gọi lại đúng handleRegenerateCode với cùng chỉ dẫn tinh chỉnh).
        // Lưu ý: tham số callback đặt tên errMsg (KHÔNG phải "message") để không che
        // khuất `message` — đối tượng ai_code ở scope ngoài của handleRegenerateCode.
        onError: (errMsg) => {
          setIsSubmitting(false);
          rollback();
          const quota = isQuotaError(errMsg);
          setMessages(prev => [...prev, {
            id: targetId + '_regenfail_' + Date.now(),
            role: 'ai_result',
            resultData: {
              type: 'error',
              kind: quota ? 'quota' : 'api',
              data: quota ? errMsg : 'Lỗi khi tạo lại/tinh chỉnh code: ' + errMsg,
              retry: quota ? { type: 'regenerate', message, refineInstruction: trimmedInstruction } : null
            },
            timestamp: new Date().toISOString()
          }]);
        },
        onAbort: () => {
          setIsSubmitting(false);
          rollback();
        }
      }
    );
  };

  // Gộp khung: code -> kết quả chạy -> nhận xét tự động của CÙNG 1 câu hỏi (đánh
  // dấu chung turnId lúc tạo) được render thành 1 khung duy nhất (.ai-turn-card),
  // thay vì 3 bong bóng rời rạc lặp lại avatar/tên dù có dừng lại chờ duyệt code
  // ở giữa. Các tin nhắn không có turnId (câu hỏi thường, Mẫu 5, lỗi lẻ...) vẫn
  // render standalone như cũ. Chỉ phần TỪ THỨ 2 trở đi trong 1 khung mới compact
  // (ẩn avatar/tên lặp lại) — phần đầu (code) vẫn hiện đầy đủ.
  const commonMessageProps = {
    onApprove: handleApprove,
    onReject: handleReject,
    onResend: handleResend,
    onRegenerate: handleRegenerateCode,
    onRegenerateText: handleRegenerateText,
    onRetry: handleRetryRequest,
    isSubmitting,
  };
  const renderMessageNodes = () => {
    const nodes = [];
    let i = 0;
    while (i < messages.length) {
      const msg = messages[i];
      if (msg.turnId) {
        const group = [msg];
        let j = i + 1;
        while (j < messages.length && messages[j].turnId === msg.turnId) {
          group.push(messages[j]);
          j++;
        }
        nodes.push(
          <div className="ai-turn-card" key={'turn_' + msg.turnId}>
            {group.map((m, idx) => (
              <AiChatMessage
                key={m.id}
                message={m}
                compact={idx > 0}
                isExecuting={executingId === m.requestId}
                {...commonMessageProps}
              />
            ))}
          </div>
        );
        i = j;
      } else {
        nodes.push(
          <AiChatMessage
            key={msg.id}
            message={msg}
            isExecuting={executingId === msg.requestId}
            {...commonMessageProps}
          />
        );
        i++;
      }
    }
    return nodes;
  };

  return (
    <div className="ai-chat-container">
      <AiHistoryPanel
        historyList={historyList}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onTogglePin={handleTogglePin}
        onRenameConversation={handleRenameConversation}
        currentConversationId={currentConversationId}
        onNewChat={handleNewChat}
      />

      <div className="ai-chat-main">
        <div className="ai-auto-comment-bar">
          <label className="ai-toggle">
            <input
              type="checkbox"
              checked={autoComment}
              onChange={(e) => setAutoComment(e.target.checked)}
            />
            <span className="ai-toggle-track"><span className="ai-toggle-thumb" /></span>
          </label>
          <span>Tự động nhận xét sau khi chạy biểu đồ</span>
        </div>

        <div className="ai-chat-messages">
          {/* Màn hình chào khi cuộc hội thoại còn trống — tránh khoảng trắng
              trơn như trước, theo đúng thói quen của Gemini/ChatGPT (icon +
              câu chào + vài gợi ý câu hỏi mẫu để bắt đầu ngay). */}
          {messages.length === 0 ? (
            <div className="ai-welcome">
              <div className="ai-welcome-icon">
                <Sparkles size={30} color="#FA6781" />
              </div>
              <h3>Bắt đầu phân tích thị trường IT Việt Nam</h3>
              <p>
                Hỏi bằng ngôn ngữ tự nhiên về lương, kỹ năng, vị trí, khu vực hay xu hướng
                tuyển dụng — AI sẽ trả lời hoặc vẽ biểu đồ THẬT dựa trên dữ liệu đã thu thập.
              </p>
              <div className="ai-welcome-starters">
                {WELCOME_STARTERS.map((s) => (
                  <button
                    key={s}
                    className="ai-welcome-starter-card"
                    onClick={() => handleSendRequest(s, null, null, null)}
                    disabled={isSubmitting}
                    type="button"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            renderMessageNodes()
          )}
          <div ref={messagesEndRef} />
        </div>

        <AiRequestForm
          onSubmit={handleSendRequest}
          isSubmitting={isSubmitting}
          onStop={handleStopGenerating}
        />
      </div>
    </div>
  );
}
