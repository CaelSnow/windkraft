"""
GLSL Shader für echtes Per-Pixel Phong Shading
===============================================

Implementiert das Phong-Beleuchtungsmodell aus der Vorlesung:
I = I_a * k_a + I_d * k_d * max(0, N·L) + I_s * k_s * max(0, R·V)^n

Unterschied zu Gouraud-Shading:
- Gouraud: Beleuchtung wird pro Vertex berechnet, dann interpoliert
- Phong: Normalen werden interpoliert, Beleuchtung pro Pixel berechnet

Vorlesungsreferenz: BRDF, Formenwahrnehmung und Reflexion
"""

# Vertex Shader für Phong Shading
PHONG_VERTEX_SHADER = """
#version 330 core

// Input Attribute
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec3 aColor;

// Output an Fragment Shader
out vec3 FragPos;      // Position im World Space
out vec3 Normal;       // Normale im World Space
out vec3 VertexColor;  // Farbe vom Vertex

// Uniforms
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat3 normalMatrix;  // transpose(inverse(model)) für korrekte Normalen

void main()
{
    // Position im World Space für Beleuchtungsberechnung
    FragPos = vec3(model * vec4(aPos, 1.0));
    
    // Normale transformieren (nicht mit model, sondern mit normalMatrix!)
    // Siehe Vorlesung: Normalen-Transformation bei nicht-uniformer Skalierung
    Normal = normalMatrix * aNormal;
    
    // Farbe weitergeben
    VertexColor = aColor;
    
    // Finale Position im Clip Space
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

# Fragment Shader für Phong Shading
PHONG_FRAGMENT_SHADER = """
#version 330 core

// Input vom Vertex Shader (interpoliert!)
in vec3 FragPos;
in vec3 Normal;
in vec3 VertexColor;

// Output Farbe
out vec4 FragColor;

// Lichtquellen (2-Licht Setup wie in opengl_utils.py)
struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    bool isDirectional;  // true = Richtungslicht, false = Punktlicht
};

// Uniforms für Beleuchtung
uniform Light lights[2];
uniform vec3 viewPos;           // Kamera-Position
uniform float shininess;        // Phong Exponent (n in der Formel)
uniform vec3 ambientGlobal;     // Globales Umgebungslicht

// Material-Parameter (aus der Vorlesung: k_a, k_d, k_s)
uniform float ka;  // Ambiente Reflexion
uniform float kd;  // Diffuse Reflexion  
uniform float ks;  // Spiegelnde Reflexion

void main()
{
    // Normale normalisieren (wichtig nach Interpolation!)
    vec3 N = normalize(Normal);
    
    // Blickrichtung V (vom Fragment zur Kamera)
    vec3 V = normalize(viewPos - FragPos);
    
    // === AMBIENTE KOMPONENTE ===
    // I_a * k_a (globales Umgebungslicht)
    vec3 ambient = ambientGlobal * ka * VertexColor;
    
    // Akkumuliere Beleuchtung von beiden Lichtquellen
    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);
    
    for (int i = 0; i < 2; i++) {
        // Lichtrichtung L (zum Licht)
        vec3 L;
        if (lights[i].isDirectional) {
            // Richtungslicht: Position ist Richtung
            L = normalize(lights[i].position);
        } else {
            // Punktlicht: Richtung vom Fragment zum Licht
            L = normalize(lights[i].position - FragPos);
        }
        
        // === DIFFUSE KOMPONENTE (Lambert) ===
        // I_d * k_d * max(0, N·L)
        // Vorlesung: Cosinus des Einfallswinkels bestimmt Helligkeit
        float NdotL = max(dot(N, L), 0.0);
        diffuse += lights[i].diffuse * kd * NdotL * VertexColor;
        
        // === SPIEGELNDE KOMPONENTE (Phong) ===
        // I_s * k_s * max(0, R·V)^n
        // Nur berechnen wenn Fläche dem Licht zugewandt ist
        if (NdotL > 0.0) {
            // Reflexionsvektor R = 2 * (N·L) * N - L
            // (aus der Vorlesung: Formenwahrnehmung, Folie 65-66)
            vec3 R = reflect(-L, N);
            
            // Phong Specular Term
            float RdotV = max(dot(R, V), 0.0);
            float spec = pow(RdotV, shininess);
            specular += lights[i].specular * ks * spec;
        }
    }
    
    // Finale Farbe: Summe aller Komponenten
    vec3 result = ambient + diffuse + specular;
    
    // Clamping auf [0, 1] (HDR würde Tonemapping erfordern)
    result = clamp(result, 0.0, 1.0);
    
    FragColor = vec4(result, 1.0);
}
"""

# Einfacher Shader für Schatten (nur Farbe, keine Beleuchtung)
SHADOW_VERTEX_SHADER = """
#version 330 core

layout(location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 shadowMatrix;  // Projektionsmatrix für Schatten

void main()
{
    // Schattenprojektion auf Bodenebene
    vec4 worldPos = model * vec4(aPos, 1.0);
    vec4 shadowPos = shadowMatrix * worldPos;
    gl_Position = projection * view * shadowPos;
}
"""

SHADOW_FRAGMENT_SHADER = """
#version 330 core

out vec4 FragColor;

uniform vec4 shadowColor;

void main()
{
    FragColor = shadowColor;
}
"""


class ShaderProgram:
    """
    Verwaltet ein GLSL Shader-Programm.
    
    Kompiliert Vertex- und Fragment-Shader und linkt sie zu einem Programm.
    """
    
    def __init__(self):
        self.program_id = None
        self.uniform_locations = {}
    
    def compile(self, vertex_source: str, fragment_source: str) -> bool:
        """
        Kompiliert und linkt die Shader.
        
        Args:
            vertex_source: GLSL Vertex Shader Code
            fragment_source: GLSL Fragment Shader Code
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        from OpenGL.GL import (
            glCreateShader, glShaderSource, glCompileShader,
            glGetShaderiv, glGetShaderInfoLog,
            glCreateProgram, glAttachShader, glLinkProgram,
            glGetProgramiv, glGetProgramInfoLog, glDeleteShader,
            GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
            GL_COMPILE_STATUS, GL_LINK_STATUS
        )
        
        # Vertex Shader kompilieren
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_source)
        glCompileShader(vertex_shader)
        
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex_shader).decode()
            print(f"FEHLER: Vertex Shader Kompilierung fehlgeschlagen:\n{error}")
            return False
        
        # Fragment Shader kompilieren
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_source)
        glCompileShader(fragment_shader)
        
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment_shader).decode()
            print(f"FEHLER: Fragment Shader Kompilierung fehlgeschlagen:\n{error}")
            return False
        
        # Programm erstellen und linken
        self.program_id = glCreateProgram()
        glAttachShader(self.program_id, vertex_shader)
        glAttachShader(self.program_id, fragment_shader)
        glLinkProgram(self.program_id)
        
        if not glGetProgramiv(self.program_id, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.program_id).decode()
            print(f"FEHLER: Shader Programm Linking fehlgeschlagen:\n{error}")
            return False
        
        # Shader können nach dem Linken gelöscht werden
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        
        print("  ✓ Phong Shader erfolgreich kompiliert")
        return True
    
    def use(self):
        """Aktiviert dieses Shader-Programm."""
        from OpenGL.GL import glUseProgram
        if self.program_id:
            glUseProgram(self.program_id)
    
    def stop(self):
        """Deaktiviert Shader (zurück zu Fixed-Function)."""
        from OpenGL.GL import glUseProgram
        glUseProgram(0)
    
    def get_uniform_location(self, name: str) -> int:
        """Cached Uniform Location Lookup."""
        from OpenGL.GL import glGetUniformLocation
        
        if name not in self.uniform_locations:
            self.uniform_locations[name] = glGetUniformLocation(self.program_id, name)
        return self.uniform_locations[name]
    
    def set_float(self, name: str, value: float):
        """Setzt einen float Uniform."""
        from OpenGL.GL import glUniform1f
        loc = self.get_uniform_location(name)
        if loc >= 0:
            glUniform1f(loc, value)
    
    def set_vec3(self, name: str, x: float, y: float, z: float):
        """Setzt einen vec3 Uniform."""
        from OpenGL.GL import glUniform3f
        loc = self.get_uniform_location(name)
        if loc >= 0:
            glUniform3f(loc, x, y, z)
    
    def set_vec4(self, name: str, x: float, y: float, z: float, w: float):
        """Setzt einen vec4 Uniform."""
        from OpenGL.GL import glUniform4f
        loc = self.get_uniform_location(name)
        if loc >= 0:
            glUniform4f(loc, x, y, z, w)
    
    def set_mat4(self, name: str, matrix):
        """Setzt einen mat4 Uniform."""
        from OpenGL.GL import glUniformMatrix4fv, GL_FALSE
        import numpy as np
        loc = self.get_uniform_location(name)
        if loc >= 0:
            mat = np.array(matrix, dtype=np.float32).flatten()
            glUniformMatrix4fv(loc, 1, GL_FALSE, mat)
    
    def set_mat3(self, name: str, matrix):
        """Setzt einen mat3 Uniform."""
        from OpenGL.GL import glUniformMatrix3fv, GL_FALSE
        import numpy as np
        loc = self.get_uniform_location(name)
        if loc >= 0:
            mat = np.array(matrix, dtype=np.float32).flatten()
            glUniformMatrix3fv(loc, 1, GL_FALSE, mat)
    
    def set_bool(self, name: str, value: bool):
        """Setzt einen bool Uniform."""
        from OpenGL.GL import glUniform1i
        loc = self.get_uniform_location(name)
        if loc >= 0:
            glUniform1i(loc, 1 if value else 0)


# Globale Shader-Instanz (lazy initialization)
_phong_shader = None
_shadow_shader = None


def get_phong_shader() -> ShaderProgram:
    """Gibt den Phong-Shader zurück (erstellt ihn bei Bedarf)."""
    global _phong_shader
    if _phong_shader is None:
        _phong_shader = ShaderProgram()
        if not _phong_shader.compile(PHONG_VERTEX_SHADER, PHONG_FRAGMENT_SHADER):
            _phong_shader = None
    return _phong_shader


def get_shadow_shader() -> ShaderProgram:
    """Gibt den Shadow-Shader zurück."""
    global _shadow_shader
    if _shadow_shader is None:
        _shadow_shader = ShaderProgram()
        if not _shadow_shader.compile(SHADOW_VERTEX_SHADER, SHADOW_FRAGMENT_SHADER):
            _shadow_shader = None
    return _shadow_shader


def check_shader_support() -> bool:
    """
    Prüft ob die GPU GLSL 3.30 unterstützt.
    
    Returns:
        True wenn Shader unterstützt werden
    """
    from OpenGL.GL import glGetString, GL_SHADING_LANGUAGE_VERSION
    
    try:
        version = glGetString(GL_SHADING_LANGUAGE_VERSION)
        if version:
            version_str = version.decode() if isinstance(version, bytes) else str(version)
            # Parse Version (z.B. "3.30" oder "4.60")
            parts = version_str.split()[0].split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            
            # Mindestens GLSL 3.30 erforderlich
            if major > 3 or (major == 3 and minor >= 30):
                print(f"  ✓ GLSL Version: {version_str} (Phong-Shader unterstützt)")
                return True
            else:
                print(f"  ⚠ GLSL Version: {version_str} (zu alt, Fallback zu Gouraud)")
                return False
    except Exception as e:
        print(f"  ⚠ Shader-Prüfung fehlgeschlagen: {e}")
    
    return False
