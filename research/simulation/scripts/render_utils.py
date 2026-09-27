import os
import re
import shutil
import subprocess
import weasyprint

def preprocess_math_html(html: str) -> str:
    """Ensure all math formulas and equations have proper LaTeX delimiters ($ or $$)."""
    # Replace unicode Greek variables that should be LaTeX
    html = html.replace('θ*', r'\theta^*')
    
    # Wrap formulas in <div class="formula"> that don't have $ delimiters
    def wrap_formula_div(match):
        attrs = match.group(1)
        content = match.group(2)
        stripped = content.strip()
        
        # If it's a quote or text without math symbols, leave it alone
        if stripped.startswith('<b>Wolpert') or stripped.startswith('MDP Tuple'):
            return match.group(0)
            
        # If it already has $$, keep it
        if '$$' in stripped:
            return match.group(0)
            
        # Check if there is a leading HTML title/label like <b>...</b><br>
        label_match = re.match(r'^(<b>.*?</b>\s*(?:<br>|&nbsp;|\s)*)([\s\S]+)$', stripped)
        if label_match:
            label = label_match.group(1).strip()
            math_body = label_match.group(2).strip().strip('$').strip()
            if ('\\' in math_body or '=' in math_body or 'E[' in math_body or 'r_t' in math_body):
                return f'<div class="formula"{attrs}>\n{label}<br>\n$${math_body}$$\n</div>'
            return match.group(0)
            
        # If no label, check if the whole body has math symbols
        clean_body = stripped.strip('$').strip()
        if ('\\' in clean_body or '=' in clean_body or 'arg\\max' in clean_body or 'E[' in clean_body):
            return f'<div class="formula"{attrs}>\n$${clean_body}$$\n</div>'
            
        return match.group(0)
        
    html = re.sub(r'<div class="formula"([^>]*)>\s*([\s\S]*?)\s*</div>', wrap_formula_div, html)
    
    # Specific un-dollared patterns identified across lectures
    def safe_wrap(content, target, replacement):
        if replacement in content or f"$${target}$$" in content:
            return content
        return content.replace(target, replacement)

    # Lecture 4 Bellman boxes
    html = safe_wrap(html,
        r'<b>Bellman Expectation Equation for V:</b> &nbsp; V^\pi(s) = \mathbb{E}_{a \sim \pi, s\' \sim P} \left[ r(s, a) + \gamma V^\pi(s\') \right]',
        r'<b>Bellman Expectation Equation for V:</b><br>$$V^\pi(s) = \mathbb{E}_{a \sim \pi, s\' \sim P} \left[ r(s, a) + \gamma V^\pi(s\') \right]$$'
    )
    html = safe_wrap(html,
        r'<b>Bellman Optimality Equation for Q:</b> &nbsp; Q^*(s, a) = \mathbb{E}_{s\' \sim P} \left[ r(s, a) + \gamma \max_{a\'} Q^*(s\', a\') \right]',
        r'<b>Bellman Optimality Equation for Q:</b><br>$$Q^*(s, a) = \mathbb{E}_{s\' \sim P} \left[ r(s, a) + \gamma \max_{a\'} Q^*(s\', a\') \right]$$'
    )
    
    # Lecture 5 EGLP lemma
    html = safe_wrap(html,
        r'<b>The Expected Grad-Log-Prob (EGLP) Lemma:</b> &nbsp; \mathbb{E}_{x \sim P_\theta} \left[ \nabla_\theta \log P_\theta(x) \right] = 0',
        r'<b>The Expected Grad-Log-Prob (EGLP) Lemma:</b><br>$$\mathbb{E}_{x \sim P_\theta} \left[ \nabla_\theta \log P_\theta(x) \right] = 0$$'
    )
    
    # Lecture 6 GAE telescoping & Jacobian
    html = safe_wrap(html,
        r'\delta_t^V = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)',
        r'$$\delta_t^V = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$$'
    )
    html = safe_wrap(html,
        r'\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = (1 - \lambda) \sum_{k=1}^\infty \lambda^{k-1} \hat{A}_t^{(k)} = \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}^V',
        r'$$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = (1 - \lambda) \sum_{k=1}^\infty \lambda^{k-1} \hat{A}_t^{(k)} = \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}^V$$'
    )
    html = safe_wrap(html,
        r'P(a|s) = P(u|s) \cdot \left| \det \left( \frac{da}{du} \right) \right|^{-1}',
        r'$$P(a|s) = P(u|s) \cdot \left| \det \left( \frac{da}{du} \right) \right|^{-1}$$'
    )
    html = safe_wrap(html,
        r'\log \pi(a|s) = \log \mu(u|s) - \sum_{i=1}^d \log \big( 1 - \tanh^2(u_i) + \epsilon \big)',
        r'$$\log \pi(a|s) = \log \mu(u|s) - \sum_{i=1}^d \log \big( 1 - \tanh^2(u_i) + \epsilon \big)$$'
    )
    
    # Lecture 8 targets & Polyak
    html = safe_wrap(html,
        r'y_t = r_t + \gamma \min \Big( Q_{\bar{\phi}_1}(s_{t+1}, \tilde{a}_{t+1}),\, Q_{\bar{\phi}_2}(s_{t+1}, \tilde{a}_{t+1}) \Big)',
        r'$$y_t = r_t + \gamma \min \Big( Q_{\bar{\phi}_1}(s_{t+1}, \tilde{a}_{t+1}),\, Q_{\bar{\phi}_2}(s_{t+1}, \tilde{a}_{t+1}) \Big)$$'
    )
    html = safe_wrap(html,
        r'J(\pi) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t) \sim \rho_\pi} \left[ r(s_t, a_t) + \alpha \, \mathcal{H}(\pi(\cdot|s_t)) \right]',
        r'$$J(\pi) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t) \sim \rho_\pi} \left[ r(s_t, a_t) + \alpha \, \mathcal{H}(\pi(\cdot|s_t)) \right]$$'
    )
    
    # Lecture 10 Kakade-Langford
    html = safe_wrap(html,
        r'J(\pi\') \ge J(\pi) + \sum_s d^\pi(s) \sum_a \pi\'(a|s) A^\pi(s, a) - C \cdot D_{\text{KL}}^{\max}(\pi, \pi\')',
        r'$$J(\pi\') \ge J(\pi) + \sum_s d^\pi(s) \sum_a \pi\'(a|s) A^\pi(s, a) - C \cdot D_{\text{KL}}^{\max}(\pi, \pi\')$$'
    )
    
    # Cleanup any multiple consecutive $ occurrences
    html = re.sub(r'\${3,}', '$$', html)
    
    return html


def render_mathjax_html(html_str: str) -> str:
    """Pipe HTML through mathjax_renderer.js to convert all $...$ and $$...$$ into vector SVGs."""
    processed_html = preprocess_math_html(html_str)
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    renderer_js = os.path.join(scripts_dir, "mathjax_renderer.js")
    
    env = dict(os.environ)
    if "NODE_PATH" not in env:
        try:
            env["NODE_PATH"] = subprocess.check_output(["npm", "root", "-g"], text=True).strip()
        except Exception:
            pass
            
    proc = subprocess.run(
        ["node", renderer_js],
        input=processed_html,
        text=True,
        capture_output=True,
        check=True,
        env=env
    )
    rendered_html = proc.stdout
    
    # Fine-tuned styling for printed MathJax SVGs
    tuning_css = """
<style>
  mjx-container[jax="SVG"] {
    display: inline-block;
    line-height: 0;
    vertical-align: 0ex;
  }
  mjx-container[jax="SVG"][display="true"] {
    display: block;
    text-align: center;
    margin: 10px 0;
  }
</style>
"""
    if "</head>" in rendered_html:
        rendered_html = rendered_html.replace("</head>", tuning_css + "</head>")
    else:
        rendered_html = tuning_css + rendered_html
        
    return rendered_html


def build_pdf(html_str: str, output_path: str, backup_path: str = None):
    """Compile publication-grade PDF with vector MathJax equations and copy to backup."""
    print("-> Converting LaTeX math to SVG via MathJax...")
    math_html = render_mathjax_html(html_str)
    
    print(f"-> Compiling PDF with WeasyPrint: {output_path}...")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    weasyprint.HTML(string=math_html).write_pdf(output_path)
    size_bytes = os.path.getsize(output_path)
    print(f"-> Saved: {output_path} ({size_bytes:,} bytes)")
    
    if backup_path:
        os.makedirs(os.path.dirname(os.path.abspath(backup_path)), exist_ok=True)
        shutil.copyfile(output_path, backup_path)
        print(f"-> Mirrored to: {backup_path}")
