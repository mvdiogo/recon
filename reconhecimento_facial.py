import cv2
import mediapipe as mp
import numpy as np
import pickle
import time
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from database import DatabaseManager
import threading
import queue

class FaceRecognitionSystem:
    def __init__(self):
        # Inicializar MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Configurar detectores
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.7
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=10,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Banco de dados
        self.db = DatabaseManager()
        
        # Cache de pessoas conhecidas
        self.pessoas_conhecidas = {}
        self.carregar_pessoas_conhecidas()
        
        # Controle de detecções recentes
        self.deteccoes_recentes = {}
        self.intervalo_deteccao = float(self.db.obter_configuracao('intervalo_deteccao') or 5)
        self.tolerancia = float(self.db.obter_configuracao('tolerancia_reconhecimento') or 0.6)
        
        # Fila para processamento assíncrono
        self.fila_processamento = queue.Queue()
        self.thread_processamento = threading.Thread(target=self._processar_deteccoes, daemon=True)
        self.thread_processamento.start()
        
        print("Sistema de reconhecimento facial inicializado!")
    
    def extrair_embedding_facial(self, imagem, landmarks):
        """Extrai embedding facial usando landmarks do MediaPipe"""
        try:
            # Converter landmarks para array numpy
            pontos = []
            h, w = imagem.shape[:2]
            
            for landmark in landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                pontos.append([x, y])
            
            pontos = np.array(pontos)
            
            # Calcular características geométricas
            # Distâncias entre pontos chave
            caracteristicas = []
            
            # Pontos importantes do rosto (índices aproximados do face mesh)
            pontos_chave = [
                10, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 125,
                142, 36, 205, 206, 207, 213, 192, 147, 187, 207, 206, 205,
                36, 142, 126, 142, 36, 205, 206, 207
            ]
            
            # Calcular distâncias entre pontos chave
            for i in range(len(pontos_chave)):
                for j in range(i+1, min(i+10, len(pontos_chave))):
                    if pontos_chave[i] < len(pontos) and pontos_chave[j] < len(pontos):
                        dist = np.linalg.norm(pontos[pontos_chave[i]] - pontos[pontos_chave[j]])
                        caracteristicas.append(dist)
            
            # Normalizar características
            caracteristicas = np.array(caracteristicas)
            if len(caracteristicas) > 0:
                caracteristicas = caracteristicas / np.linalg.norm(caracteristicas)
            
            return caracteristicas
            
        except Exception as e:
            print(f"Erro ao extrair embedding: {e}")
            return None
    
    def carregar_pessoas_conhecidas(self):
        """Carrega pessoas conhecidas do banco de dados"""
        try:
            pessoas = self.db.obter_pessoas_conhecidas()
            self.pessoas_conhecidas = {}
            
            for pessoa in pessoas:
                pessoa_id, nome, idade, sexo, etnia, telefone, encoding_blob = pessoa
                if encoding_blob:
                    try:
                        encoding = pickle.loads(encoding_blob)
                        self.pessoas_conhecidas[pessoa_id] = {
                            'nome': nome,
                            'idade': idade,
                            'sexo': sexo,
                            'etnia': etnia,
                            'telefone': telefone,
                            'encoding': encoding
                        }
                    except Exception as e:
                        print(f"Erro ao carregar encoding da pessoa {nome}: {e}")
            
            print(f"Carregadas {len(self.pessoas_conhecidas)} pessoas conhecidas")
            
        except Exception as e:
            print(f"Erro ao carregar pessoas conhecidas: {e}")
    
    def reconhecer_pessoa(self, encoding_face):
        """Reconhece uma pessoa comparando com o banco de dados"""
        if encoding_face is None or len(self.pessoas_conhecidas) == 0:
            return None, 0.0
        
        melhor_match = None
        melhor_confianca = 0.0
        
        try:
            for pessoa_id, dados in self.pessoas_conhecidas.items():
                encoding_conhecido = dados['encoding']
                
                # Calcular similaridade
                if len(encoding_face) == len(encoding_conhecido):
                    similaridade = cosine_similarity([encoding_face], [encoding_conhecido])[0][0]
                    
                    if similaridade > self.tolerancia and similaridade > melhor_confianca:
                        melhor_confianca = similaridade
                        melhor_match = pessoa_id
            
            return melhor_match, melhor_confianca
            
        except Exception as e:
            print(f"Erro no reconhecimento: {e}")
            return None, 0.0
    
    def _processar_deteccoes(self):
        """Thread para processar detecções de forma assíncrona"""
        while True:
            try:
                item = self.fila_processamento.get(timeout=1)
                if item is None:
                    break
                
                encoding, timestamp = item
                pessoa_id, confianca = self.reconhecer_pessoa(encoding)
                
                if pessoa_id:
                    # Pessoa conhecida encontrada
                    agora = datetime.now()
                    chave_deteccao = f"conhecida_{pessoa_id}"
                    
                    # Verificar se já foi detectada recentemente
                    if (chave_deteccao not in self.deteccoes_recentes or 
                        (agora - self.deteccoes_recentes[chave_deteccao]).seconds >= self.intervalo_deteccao):
                        
                        self.db.registrar_presenca(pessoa_id, 'conhecida', confianca)
                        self.deteccoes_recentes[chave_deteccao] = agora
                        
                        nome = self.pessoas_conhecidas[pessoa_id]['nome']
                        print(f"✓ PRESENÇA REGISTRADA: {nome} (confiança: {confianca:.2f})")
                else:
                    # Pessoa desconhecida
                    pessoa_id, codigo_temp = self.db.adicionar_pessoa_desconhecida(pickle.dumps(encoding))
                    self.db.registrar_presenca(pessoa_id, 'desconhecida', 0.0)
                    print(f"? PESSOA DESCONHECIDA: {codigo_temp}")
                
                self.fila_processamento.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Erro no processamento: {e}")
    
    def processar_frame(self, frame):
        """Processa um frame da webcam"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detectar rostos
        results_detection = self.face_detection.process(rgb_frame)
        results_mesh = self.face_mesh.process(rgb_frame)
        
        if results_detection.detections:
            for detection in results_detection.detections:
                # Desenhar caixa de detecção
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                           int(bboxC.width * iw), int(bboxC.height * ih)
                
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Confiança: {detection.score[0]:.2f}", 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Processar landmarks para reconhecimento
        if results_mesh.multi_face_landmarks:
            for face_landmarks in results_mesh.multi_face_landmarks:
                # Extrair embedding
                encoding = self.extrair_embedding_facial(rgb_frame, face_landmarks)
                
                if encoding is not None:
                    # Adicionar à fila de processamento
                    self.fila_processamento.put((encoding, datetime.now()))
                
                # Desenhar landmarks (opcional, pode ser removido para performance)
                self.mp_drawing.draw_landmarks(
                    frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS,
                    None, self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                )
        
        return frame
    
    def iniciar_reconhecimento(self, camera_index=0):
        """Inicia o sistema de reconhecimento em tempo real"""
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("Erro: Não foi possível abrir a câmera")
            return
        
        print("Sistema iniciado! Pressione 'q' para sair, 'r' para recarregar pessoas conhecidas")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Erro ao capturar frame")
                    break
                
                # Processar frame
                frame_processado = self.processar_frame(frame)
                
                # Mostrar informações na tela
                cv2.putText(frame_processado, f"Pessoas conhecidas: {len(self.pessoas_conhecidas)}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame_processado, f"Tolerancia: {self.tolerancia}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame_processado, "Pressione 'q' para sair, 'r' para recarregar", 
                           (10, frame_processado.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('Sistema de Reconhecimento Facial - Igreja', frame_processado)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    print("Recarregando pessoas conhecidas...")
                    self.carregar_pessoas_conhecidas()
                
        except KeyboardInterrupt:
            print("\nSistema interrompido pelo usuário")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            # Parar thread de processamento
            self.fila_processamento.put(None)
    
    def adicionar_pessoa_do_video(self, nome, idade, sexo, etnia, telefone, camera_index=0):
        """Adiciona uma nova pessoa capturando da webcam"""
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("Erro: Não foi possível abrir a câmera")
            return False
        
        print(f"Capturando rosto para {nome}...")
        print("Posicione o rosto na tela e pressione ESPAÇO para capturar, 'q' para cancelar")
        
        encodings_capturados = []
        
        try:
            while len(encodings_capturados) < 5:  # Capturar 5 amostras
                ret, frame = cap.read()
                if not ret:
                    break
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        # Desenhar landmarks
                        self.mp_drawing.draw_landmarks(
                            frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS
                        )
                        
                        # Mostrar instruções
                        cv2.putText(frame, f"Capturado: {len(encodings_capturados)}/5", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(frame, "ESPACO: Capturar | Q: Cancelar", 
                                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Captura de Rosto', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' ') and results.multi_face_landmarks:
                    # Capturar encoding
                    for face_landmarks in results.multi_face_landmarks:
                        encoding = self.extrair_embedding_facial(rgb_frame, face_landmarks)
                        if encoding is not None:
                            encodings_capturados.append(encoding)
                            print(f"Amostra {len(encodings_capturados)} capturada!")
                            break
                elif key == ord('q'):
                    print("Captura cancelada")
                    return False
            
            if len(encodings_capturados) >= 3:
                # Calcular encoding médio
                encoding_medio = np.mean(encodings_capturados, axis=0)
                
                # Salvar no banco de dados
                pessoa_id = self.db.adicionar_pessoa_conhecida(
                    nome, idade, sexo, etnia, telefone, pickle.dumps(encoding_medio)
                )
                
                print(f"Pessoa {nome} adicionada com sucesso! ID: {pessoa_id}")
                
                # Recarregar cache
                self.carregar_pessoas_conhecidas()
                return True
            else:
                print("Não foi possível capturar amostras suficientes")
                return False
                
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    sistema = FaceRecognitionSystem()
    sistema.iniciar_reconhecimento()

